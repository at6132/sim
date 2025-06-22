import os
import json
import random
import math
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import redis

# System imports
from .environment import EnvironmentalSystem, Environment
from .terrain import TerrainSystem, TerrainType, OceanCurrent
from .climate import ClimateSystem, ClimateType
from .resources import ResourceSystem, ResourceType, Resource
from .plants import PlantSystem, Plant, PlantType
from .animals import AnimalSystem, Animal
from .technology import TechnologySystem, Technology
from .society import SocietySystem, Society
from .transportation import TransportationSystem, TransportationType
from .discovery import DiscoverySystem, Discovery
from .agents import AgentSystem, Agent
from .biology import BiologicalSystem
from .weather import WeatherType, WeatherState, WeatherSystem
from .llm import AgentCognition
from .marine import MarineSystem, Marine
from .natural_disaster import NaturalDisasterSystem
from .physics import PhysicsSystem

# Utility imports
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class World:
    @classmethod
    def load_from_save(cls, logger):
        """Load the most recent world state from disk."""
        save_dir = os.path.join('simulation_saves', 'current_world')
        world_state_path = os.path.join(save_dir, 'world_state.json')
        if not os.path.exists(world_state_path):
            logger.info("No save found, creating new world")
            return None
        try:
            with open(world_state_path, 'r') as f:
                world_state = json.load(f)
            # Create new world instance
            world = cls(logger)
            # Restore world state
            world.current_tick = world_state['current_tick']
            world.game_time = datetime.fromisoformat(world_state['game_time'])
            world.simulation_time = world_state['simulation_time']
            world.day = world_state['day']
            world.year = world_state['year']
            world.events = world_state['events']
            # Load agent states
            agents_path = os.path.join(save_dir, 'agents.json')
            if os.path.exists(agents_path):
                with open(agents_path, 'r') as f:
                    agent_states = json.load(f)
                # Restore agents
                for agent_id, agent_data in agent_states.items():
                    agent = Agent(
                        id=agent_data['id'],
                        name=agent_data['name'],
                        position=agent_data['position'],
                        health=agent_data['health'],
                        energy=agent_data['energy'],
                        hunger=agent_data['hunger'],
                        thirst=agent_data['thirst'],
                        age=agent_data['age'],
                        skills=agent_data['skills'],
                        inventory=agent_data['inventory'],
                        last_action=agent_data['last_action'],
                        world=world,
                        logger=logger
                    )
                    world.agents.agents[agent_id] = agent
            logger.info(f"Loaded world state from tick {world.current_tick}")
            return world
        except Exception as e:
            logger.error(f"Error loading world state: {e}")
            logger.error(traceback.format_exc())
            return None

    def __init__(self, logger):
        """Initialize a new world."""
        self.logger = logger
        # Set world coordinates to match real Earth dimensions
        self.min_longitude = -180
        self.max_longitude = 180
        self.min_latitude = -90
        self.max_latitude = 90

        # World width/height in degrees
        self.width = self.max_longitude - self.min_longitude
        self.height = self.max_latitude - self.min_latitude

        self.longitude_resolution = 1.0
        self.latitude_resolution = 1.0
        self.simulation_time = 0
        self.current_tick = 0
        self.game_time = datetime.now()
        self.real_time_start = datetime.now()
        self.game_time_start = datetime.now()
        # 48 game seconds pass per real second (1 day every 30 minutes)
        self.time_scale = 48.0
        self.day = 1
        self.year = 1
        self.running = False
        self.events = []
        self.explored_areas = set()
        self.discovered_resources = set()
        self.known_territories = set()
        
        # Initialize save directories
        self.save_dir = "simulation_saves"
        self.db_dir = os.path.join(self.save_dir, "data")
        os.makedirs(self.save_dir, exist_ok=True)
        os.makedirs(self.db_dir, exist_ok=True)
        os.makedirs(os.path.join(self.save_dir, "current_world"), exist_ok=True)
        logger.info(f"Initialized save directories: {self.save_dir} and {self.db_dir}")

        # Initialize Redis client for world state persistence
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
            # Test connection
            self.redis.ping()
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except Exception as e:
            self.redis = None
            logger.error(f"Failed to connect to Redis: {e}")
        
        # Initialize systems in dependency order
        self.climate = ClimateSystem(self)
        self.terrain = TerrainSystem(self)
        self.resources = ResourceSystem(self)
        self.plants = PlantSystem(self)
        self.animals = AnimalSystem(self)
        self.marine = MarineSystem(self)
        self.technology = TechnologySystem(self)
        self.society = SocietySystem(self)
        self.transportation = TransportationSystem(self)
        self.weather = WeatherSystem(self)
        self.disasters = NaturalDisasterSystem(self)
        self.physics = PhysicsSystem(self)
        self.environment = EnvironmentalSystem(self)
        self.agents = AgentSystem(self)
        self.discovery = DiscoverySystem(self)
        
        logger.info("World initialized successfully")
        
    def _initialize_world(self):
        """Initialize all world systems."""
        logger.info("Initializing world systems...")
        
        # Initialize systems in order of dependency
        logger.info("Initializing terrain system...")
        self.terrain.initialize_terrain()
        logger.info("Terrain system initialized")
        
        logger.info("Initializing environment system...")
        self.environment.initialize_system()
        logger.info("Environment system initialized")
        
        logger.info("Initializing climate system...")
        self.climate.initialize_earth_climate()
        logger.info("Climate system initialized")
        
        logger.info("Initializing resource system...")
        self.resources.initialize_resources()
        logger.info("Resource system initialized")
        
        logger.info("Initializing agent system...")
        self.agents.initialize_agents()  # Just initialize the system, don't create agents yet
        logger.info("Agent system initialized")
        
        # Initialize remaining systems
        logger.info("Initializing society system...")
        self.society.initialize_society()
        logger.info("Society system initialized")
        
        logger.info("Initializing transportation system...")
        self.transportation.initialize_transportation()
        logger.info("Transportation system initialized")
        
        logger.info("Initializing plant system...")
        self.plants.initialize_plants()
        logger.info("Plant system initialized")
        
        logger.info("Initializing animal system...")
        self.animals.initialize_animal_system()
        logger.info("Animal system initialized")
        
        logger.info("Initializing marine system...")
        self.marine.initialize_marine_system()
        logger.info("Marine system initialized")
        
        logger.info("Initializing biological system...")
        self.biology = BiologicalSystem(self)
        self.biology.initialize_system()
        logger.info("Biological system initialized")
        
        logger.info("Initializing weather system...")
        self.weather.initialize_weather_systems()
        logger.info("Weather system initialized")

        logger.info("Initializing natural disaster system...")
        self.disasters.initialize_system()
        logger.info("Natural disaster system initialized")
        
        logger.info("Initializing technology system...")
        self.technology.initialize_technology()
        logger.info("Technology system initialized")
        
        logger.info("Initializing discovery system...")
        self.discovery._initialize_discoveries()
        logger.info("Discovery system initialized successfully")
        
        # Verify initialization
        self._verify_initialization()
        
        logger.info("World initialization complete")

    @property
    def settlements(self):
        """Convenience accessor for settlements."""
        return self.society.settlements

    def _verify_initialization(self) -> bool:
        """Verify that all systems are properly initialized."""
        self.logger.info("Verifying world initialization...")
        
        # Check environment
        if not hasattr(self, 'environment') or not self.environment:
            self.logger.error("Environment not initialized")
            return False
            
        # Check terrain
        if not hasattr(self, 'terrain') or not self.terrain:
            self.logger.error("Terrain not initialized")
            return False
            
        # Check climate
        if not hasattr(self, 'climate') or not self.climate:
            self.logger.error("Climate not initialized")
            return False
            
        # Check resources
        if not hasattr(self, 'resources') or not self.resources:
            self.logger.error("Resources not initialized")
            return False
            
        # Check plants
        if not hasattr(self, 'plants') or not self.plants:
            self.logger.error("Plants not initialized")
            return False
            
        # Check animals
        if not hasattr(self, 'animals') or not self.animals:
            self.logger.error("Animals not initialized")
            return False
            
        # Check marine
        if not hasattr(self, 'marine') or not self.marine:
            self.logger.error("Marine not initialized")
            return False
            
        # Check technology
        if not hasattr(self, 'technology') or not self.technology:
            self.logger.error("Technology system not properly initialized")
            return False
            
        # Check society
        if not hasattr(self, 'society') or not self.society:
            self.logger.error("Society not initialized")
            return False
            
        # Check transportation
        if not hasattr(self, 'transportation') or not self.transportation:
            self.logger.error("Transportation not initialized")
            return False
            
        # Check discovery
        if not hasattr(self, 'discovery') or not self.discovery:
            self.logger.error("Discovery not initialized")
            return False
            
        # Check events
        if not hasattr(self, 'events'):
            self.logger.error("Events not initialized")
            return False
            
        # Check game time
        if not hasattr(self, 'game_time'):
            self.logger.error("Game time not initialized")
            return False
            
        # Check required technology types
        required_types = {'mining', 'farming', 'hunting', 'fishing', 'construction', 'medicine', 'transportation', 'communication', 'weaponry', 'defense'}
        if not all(tech in self.technology.technologies for tech in required_types):
            self.logger.error("Not all required technology types initialized")
            return False
            
        self.logger.info("World initialization verification successful")
        return True

    def get_current_game_time(self) -> datetime:
        """Get current game time as datetime."""
        real_time_elapsed = datetime.now() - self.real_time_start
        # Scale the elapsed real time and add it to the start of the game clock
        scaled_seconds = real_time_elapsed.total_seconds() * self.time_scale
        game_time_elapsed = timedelta(seconds=scaled_seconds)
        return self.game_time_start + game_time_elapsed
        
    def update(self, time_delta: float):
        """Update world state. Each tick is 1 second in game."""
        self.simulation_time += 1
        self.current_tick += 1
        self.game_time += timedelta(seconds=1)

        # Log the tick number and current game time
        self.logger.info(
            f"Tick {self.current_tick}: game time {self.game_time.isoformat()}"
        )
        
        # Increment day every 86,400 ticks (1 day in game)
        if self.current_tick % 86400 == 0:
            self.day += 1
            self.logger.info(f"New day in game: Day {self.day}")
        
        # Update all systems with the new time delta (1 second)
        self.terrain.update(1)
        self.climate.update(1)
        self.resources.update(1)
        self.plants.update(self.simulation_time, self.get_world_state())
        self.animals.update(1)
        self.marine.update(1)
        self.technology.update(1)
        self.society.update(1)
        self.transportation.update(1)
        self.weather.update(1)
        self.disasters.update(1)
        self.physics.update(1)
        self.environment.update(1)
        self.agents.update(1)

        # Persist world state to Redis for frontend consumption
        if self.redis:
            try:
                self.redis.set('world_state', json.dumps(self.get_world_state()))
            except Exception as e:
                self.logger.error(f"Failed to update Redis state: {e}")
        
        # Save state every 1000 ticks
        if self.current_tick % 1000 == 0:
                self._save_state()
        
    def get_world_state(self) -> Dict:
        """Get current world state."""
        return {
            "time": self.game_time.isoformat(),
            "simulation_time": self.simulation_time,
            "tick": self.current_tick,
            "time_scale": self.time_scale,
            "real_time_start": self.real_time_start.isoformat(),
            "game_time_start": self.game_time_start.isoformat(),
            "environment": self.environment.get_state(),
            "terrain": self.terrain.get_state(),
            "climate": self.climate.get_state(),
            "resources": self.resources.get_state(),
            "agents": {str(agent_id): agent.get_state() for agent_id, agent in self.agents.agents.items()},
            "society": self.society.get_state(),
            "transportation": self.transportation.get_state(),
            "plants": self.plants.get_state(),
            "animals": self.animals.get_state(),
            "marine": self.marine.get_state(),
            "weather": self.weather.get_state(),
            "disasters": self.disasters.get_state(),
            "technology": self.technology.get_state(),
            "explored_areas": [f"{lon},{lat}" for lon, lat in self.explored_areas],
            "discovered_resources": list(self.discovered_resources),
            "known_territories": list(self.known_territories)
        }

    def get_state(self) -> Dict:
        """Get the current world state."""
        try:
            return {
                'current_tick': self.current_tick,
                'agents': [agent.get_state() for agent in self.agents],
                'terrain': self.terrain.get_state(),
                'climate': self.climate.get_state(),
                'resources': self.resources.get_state(),
                'plants': self.plants.get_state(),
                'animals': self.animals.get_state(),
                'marine': self.marine.get_state(),
                'technology': self.technology.get_state(),
                'society': self.society.get_state(),
                'transportation': self.transportation.get_state(),
                'weather': self.weather.get_state()
            }
        except Exception as e:
            self.logger.error(f"Error getting world state: {e}")
            self.logger.error(traceback.format_exc())
            return {}

    def to_dict(self) -> Dict:
        """Convert world state to dictionary."""
        return {
            "width": self.width,
            "height": self.height,
            "longitude_resolution": self.longitude_resolution,
            "latitude_resolution": self.latitude_resolution,
            "min_longitude": self.min_longitude,
            "max_longitude": self.max_longitude,
            "min_latitude": self.min_latitude,
            "max_latitude": self.max_latitude,
            "simulation_time": self.simulation_time,
            "current_tick": self.current_tick,
            "game_time": self.game_time.isoformat(),
            "day": self.day,
            "year": self.year,
            "explored_areas": [f"{lon},{lat}" for lon, lat in self.explored_areas],
            "events": self.events,
            "terrain": self.terrain.get_state(),
            "climate": self.climate.get_state(),
            "resources": self.resources.get_state(),
            "society": self.society.get_state(),
            "transportation": self.transportation.get_state(),
            "plants": self.plants.get_state(),
            "animals": self.animals.get_state(),
            "marine": self.marine.get_state(),
            "weather": self.weather.get_state(),
            "disasters": self.disasters.get_state(),
            "environment": self.environment.get_state(),
            "discovery": self.discovery.get_state()
        }
        
    def spawn_initial_agents(self, count: int = 2):
        """Spawn the first two agents near Passaic, NJ."""

        base_lon, base_lat = -74.1295, 40.8574

        # Spawn first agent without predefined name
        male_lon, male_lat = self.get_spawn_location(base_lon, base_lat, radius=0.01)
        first_id = self.agents.create_agent(
            longitude=male_lon,
            latitude=male_lat,
            name=None,
            gender="unknown",
        )
        self.physics.register_agent(self.agents.get_agent(first_id))

        # Spawn second agent without predefined name
        female_lon, female_lat = self.get_spawn_location(base_lon, base_lat, radius=0.01)
        second_id = self.agents.create_agent(
            longitude=female_lon,
            latitude=female_lat,
            name=None,
            gender="unknown",
        )
        self.physics.register_agent(self.agents.get_agent(second_id))

        # Create an initial farming field near the spawn area
        field_id = self.plants.create_field(base_lon, base_lat, size=1.0)
        self.plants.plant_seed(
            PlantType.WHEAT,
            base_lon,
            base_lat,
            planted_by=first_id,
            field_id=field_id,
        )

        self.logger.info(
            f"Spawned initial agents at ({male_lon:.2f},{male_lat:.2f}) and ({female_lon:.2f},{female_lat:.2f})"
        )

    def _spawn_child(self, parent_id: str) -> Optional[str]:
        """Spawn a child agent from a parent."""
        parent = self.agents.get_agent(parent_id)
        if not parent:
            return None
            
        # Get spawn location near parent
        lon, lat = self.get_spawn_location(
            center_lon=parent.longitude,
            center_lat=parent.latitude,
            radius=0.1  # Spawn very close to parent
        )
        
        # Create child through agent system
        child_id = self.agents.create_agent(
            longitude=lon,
            latitude=lat,
            parent_id=parent_id
        )

        if child_id:
            self.physics.register_agent(self.agents.get_agent(child_id))

        if child_id:
            # Initialize cognition system for the child
            self.cognition_systems[child_id] = AgentCognition(child_id)
        
        if child_id:
            self.logger.info(f"Spawned child agent {child_id} from parent {parent_id}")
            
        return child_id

    def verify_initialization(self) -> bool:
        """Verify that all systems are properly initialized."""
        logger.info("Verifying world initialization...")
        
        # Verify terrain system
        if not hasattr(self.terrain, 'terrain_data') or not self.terrain.terrain_data:
            logger.error("Terrain system not properly initialized")
            return False
            
        # Verify climate system
        if not hasattr(self.climate, 'temperature_map') or not self.climate.temperature_map.any():
            logger.error("Climate system not properly initialized")
            return False
            
        # Verify resource system
        if not hasattr(self.resources, 'resources') or not self.resources.resources:
            logger.error("Resource system not properly initialized")
            return False
            
        # Verify plant system
        if not hasattr(self.plants, 'plants') or not self.plants.plants:
            logger.error("Plant system not properly initialized")
            return False
            
        # Verify animal system
        if not hasattr(self.animals, 'creatures') or not self.animals.creatures:
            logger.error("Animal system not properly initialized")
            return False
            
        # Verify marine system
        if not hasattr(self.marine, 'creatures') or not self.marine.creatures:
            logger.error("Marine system not properly initialized")
            return False
            
        # Verify technology system
        if not hasattr(self.technology, 'technology_tree') or not self.technology.technology_tree:
            logger.error("Technology system not properly initialized")
            return False
            
        # Verify society system
        if not hasattr(self.society, 'social_groups') or not self.society.social_groups:
            logger.error("Society system not properly initialized")
            return False
            
        # Verify transportation system
        if not hasattr(self.transportation, 'roads') or not self.transportation.roads:
            logger.error("Transportation system not properly initialized")
            return False
            
        logger.info("World initialization verified successfully")
        return True

    def get_terrain_at(self, x: float, y: float) -> TerrainType:
        """Get terrain type at given coordinates."""
        return self.terrain.get_terrain_at(x, y)
        
    def get_climate_at(self, longitude: float, latitude: float) -> ClimateType:
        """Get climate type at given coordinates."""
        return self.climate.get_climate_at(longitude, latitude)
        
    def get_weather_at(self, longitude: float, latitude: float) -> Dict:
        """Get weather conditions at given coordinates."""
        return self.weather.get_weather_at(longitude, latitude)
        
    def get_resources_at(self, longitude: float, latitude: float) -> Dict:
        """Get resources available at given coordinates."""
        return self.resources.get_resources_at(longitude, latitude)
        
    def is_valid_position(self, longitude: float, latitude: float) -> bool:
        """Check if coordinates are within valid Earth bounds."""
        return (self.min_longitude <= longitude <= self.max_longitude and
                self.min_latitude <= latitude <= self.max_latitude)
                
    def get_spawn_location(self, center_lon: float = -74.1295, center_lat: float = 40.8568, radius: float = 0.01) -> Tuple[float, float]:
        """Get a random spawn location within the initial spawn area.
        Default coordinates are for Passaic, NJ (-74.1295, 40.8568)
        """
        # Generate random point within radius
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius)
        
        # Convert to longitude/latitude
        lon = center_lon + (distance * math.cos(angle))
        lat = center_lat + (distance * math.sin(angle))
        
        # Ensure coordinates are valid
        lon = max(self.min_longitude, min(self.max_longitude, lon))
        lat = max(self.min_latitude, min(self.max_latitude, lat))
        
        return (lon, lat)

    def get_distance(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """Calculate distance between two points in kilometers using the Haversine formula."""
        from math import radians, sin, cos, sqrt, atan2
        
        # Convert to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        radius = 6371  # Earth's radius in kilometers
        
        return radius * c

    def get_tile_size(self, latitude: float) -> Tuple[float, float]:
        """Get the size of a tile at a given latitude in km."""
        # At the equator, 1 degree of longitude = 111.32 km
        # At other latitudes, multiply by cos(latitude)
        lat_rad = math.radians(latitude)
        lon_size = 111.32 * math.cos(lat_rad)  # km per degree of longitude
        lat_size = 111.32  # km per degree of latitude
        
        return (lon_size, lat_size)

    def get_current_at(self, longitude: float, latitude: float) -> Optional[OceanCurrent]:
        """Get ocean current at given coordinates."""
        return self.terrain.get_current_at(longitude, latitude)
        
    def get_elevation_at(self, longitude: float, latitude: float) -> float:
        """Get elevation at given coordinates in meters."""
        return self.terrain.get_elevation_at(longitude, latitude)
        
    def get_temperature_at(self, longitude: float, latitude: float) -> float:
        """Get temperature at given coordinates in Celsius."""
        return self.climate.get_temperature_at(longitude, latitude)
        
    def get_precipitation_at(self, longitude: float, latitude: float) -> float:
        """Get precipitation at given coordinates in mm/year."""
        return self.climate.get_precipitation_at(longitude, latitude)
        
    def get_tidal_range_at(self, longitude: float, latitude: float) -> float:
        """Get tidal range at given coordinates in meters."""
        return self.terrain.get_tidal_range_at(longitude, latitude)
        
    def get_seasonal_factors_at(self, longitude: float, latitude: float) -> Dict[str, float]:
        """Get seasonal factors at given coordinates."""
        return self.terrain.get_seasonal_factors_at(longitude, latitude)

    def _generate_name(self) -> Tuple[str, str]:
        """Generate a name based on developing language and culture."""
        # Get current language development level
        language_level = self.society.get_language_development()
        
        # Basic phonemes for early language
        early_phonemes = {
            "vowels": ["a", "e", "i", "o", "u"],
            "consonants": ["b", "d", "g", "k", "m", "n", "p", "t", "v", "z"]
        }
        
        # More complex phonemes for developed language
        developed_phonemes = {
            "vowels": ["a", "e", "i", "o", "u", "ai", "ei", "ou", "ie"],
            "consonants": ["b", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "r", "s", "t", "v", "w", "y", "z", "ch", "sh", "th"]
        }
        
        # Choose phonemes based on language development
        phonemes = developed_phonemes if language_level > 0.5 else early_phonemes
        
        # Generate first name structure based on language development
        if language_level < 0.3:
            # Very early language: simple consonant-vowel pattern
            first_name = random.choice(phonemes["consonants"]) + random.choice(phonemes["vowels"])
        elif language_level < 0.6:
            # Developing language: consonant-vowel-consonant pattern
            first_name = (random.choice(phonemes["consonants"]) + 
                       random.choice(phonemes["vowels"]) + 
                       random.choice(phonemes["consonants"]))
        else:
            # Developed language: more complex patterns
            if random.random() < 0.5:
                # Two syllables
                first_name = (random.choice(phonemes["consonants"]) + 
                           random.choice(phonemes["vowels"]) + 
                           random.choice(phonemes["consonants"]) + 
                           random.choice(phonemes["vowels"]))
            else:
                # Three syllables
                first_name = (random.choice(phonemes["consonants"]) + 
                           random.choice(phonemes["vowels"]) + 
                           random.choice(phonemes["consonants"]) + 
                           random.choice(phonemes["vowels"]) + 
                           random.choice(phonemes["consonants"]))
        
        # Generate last name based on tribal affiliation
        last_name = self._generate_last_name()
        
        # Capitalize first letter of both names
        return first_name.capitalize(), last_name.capitalize()

    def _generate_last_name(self) -> str:
        """Generate a last name based on tribal affiliation and cultural development."""
        # Get current cultural development level
        culture_level = self.society.get_cultural_development()
        
        # Early tribal names
        early_tribal_names = [
            "River", "Mountain", "Forest", "Valley", "Hill", "Lake", "Stone", "Sky",
            "Wind", "Sun", "Moon", "Star", "Fire", "Water", "Earth"
        ]
        
        # More complex tribal names for developed cultures
        developed_tribal_names = [
            "Swift", "Strong", "Wise", "Brave", "Noble", "Bright", "Clear", "Deep",
            "High", "Light", "Dark", "Wild", "Calm", "Sharp", "Quick"
        ]
        
        # Choose name pool based on cultural development
        name_pool = developed_tribal_names if culture_level > 0.5 else early_tribal_names
        
        # Generate tribal name
        base_name = random.choice(name_pool)
        
        # Add tribal suffix based on cultural development
        if culture_level > 0.7:
            suffixes = ["son", "sen", "berg", "stein", "man", "er", "ian", "ski"]
            if random.random() < 0.3:
                base_name += random.choice(suffixes)
        
        return base_name

    def _generate_child_name(self, mother: Agent, father: Agent) -> Tuple[str, str]:
        """Generate a name for a child based on parents' culture and language."""
        # Get parents' social group
        mother_group = None
        father_group = None
        for group in self.society.social_groups.values():
            if mother.id in group.members:
                mother_group = group
            if father.id in group.members:
                father_group = group
                
        # If parents are in the same group, use that group's naming conventions
        if mother_group and mother_group == father_group:
            # Use group's language and culture for naming
            language_level = mother_group.language_development
            culture = mother_group.culture
            
            # Generate first name
            first_name = self._generate_name()[0]  # Get just the first name
            
            # Determine last name
            if culture == "tribal":
                # Tribal names might include nature elements
                last_name = self._generate_last_name()
            elif culture == "agricultural":
                # Agricultural names might reference seasons or crops
                season_elements = ["Spring", "Summer", "Harvest", "Seed"]
                if random.random() < 0.3:
                    last_name = random.choice(season_elements)
                else:
                    last_name = father.last_name  # Default to father's last name
            elif culture == "urban":
                # Urban names might be more complex
                if random.random() < 0.4:
                    last_name = self._generate_last_name()
                else:
                    last_name = father.last_name  # Default to father's last name
            else:
                last_name = father.last_name  # Default to father's last name
                    
            return first_name, last_name
        else:
            # If parents are from different groups, combine elements
            first_name = self._generate_name()[0]
            last_name = father.last_name  # Default to father's last name
            return first_name, last_name

    def _get_agent_state(self, agent: Agent) -> Dict:
        """Get current state of agent for the frontend."""
        return {
            "id": agent.id,
            "name": agent.name,
            "position": [float(agent.position[0]), float(agent.position[1])],
            "age": agent.age,
            "life_stage": agent.life_stage.value,
            "genes": agent.genes,
            "needs": agent.needs,
            "discovered_concepts": agent.discovered_concepts,
            "understanding_levels": agent.understanding_levels,
            "hypotheses": agent.hypotheses,
            "relationships": agent.relationships,
            "social_roles": agent.social_roles,
            "customs": agent.customs,
            "tools": agent.tools,
            "techniques": agent.techniques,
            "remedies": agent.remedies,
            "emotional_concepts": agent.emotional_concepts,
            "health_concepts": agent.health_concepts,
            "philosophy": agent.philosophy,
            "emotions": agent.emotions,
            "cognition": agent.cognition,
            "inventory": agent.inventory,
            "diseases": agent.diseases,
            "injuries": agent.injuries,
            "family_structure": agent.family_structure,
            "recent_memories": agent.recent_memories,
            "moral_alignment": agent.moral_alignment,
            "crisis_state": agent.crisis_state,
            "crimes_committed": agent.crimes_committed,
            "enemies": agent.enemies,
            "allies": agent.allies,
            "social_state": agent.social_state,
            "environment": {
                "terrain_type": agent.environment.terrain_type.value,
                "resources": {f"{k[0]},{k[1]}": v for k, v in agent.environment.resources.items()},
                "climate": agent.environment.climate.value,
                "weather": agent.environment.weather.value
            }
        }

    def _get_explored_area(self, position: Tuple[float, float]) -> List[str]:
        """Get explored area around a position."""
        explored_areas = []
        x, y = position
        radius = 5  # Exploration radius
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                new_x = x + dx
                new_y = y + dy
                if (new_x, new_y) in self.explored_areas:
                    explored_areas.append(f"{new_x},{new_y}")
        
        return explored_areas

    def _apply_agent_action(self, agent: Agent, action: Dict):
        """Apply an agent's action to the world."""
        if action["type"] == "move":
            # Calculate movement based on agent's speed and terrain
            speed = agent.genes.get("speed", 1.0)
            terrain = self.environment.get_terrain_at(*agent.position)
            terrain_modifier = {
                "plains": 1.0,
                "forest": 0.7,
                "mountain": 0.5,
                "desert": 0.8,
                "water": 0.3
            }.get(terrain.value, 1.0)
            
            
            # Calculate new position
            dx = random.randint(-1, 1) * speed * terrain_modifier
            dy = random.randint(-1, 1) * speed * terrain_modifier
            new_x = max(0, min(self.environment.width - 1, int(agent.position[0] + dx)))
            new_y = max(0, min(self.environment.height - 1, int(agent.position[1] + dy)))
            
            # Update position and mark as explored
            agent.position = (new_x, new_y)
            self.explored_areas.add((new_x, new_y))
            
            # Generate resources at new location if needed
            terrain = self.environment.get_terrain_at(new_x, new_y)
            if (new_x, new_y) not in self.resources.resources:
                self.resources.generate_resources(new_x, new_y, terrain.value)
            
            self.log_event("agent_moved", {
                "agent_id": agent.id,
                "from": agent.position,
                "to": (new_x, new_y),
                "terrain": terrain.value
            })
            
        elif action["type"] == "gather":
            # Gather resources at current position
            resource_type = ResourceType(action["resource"])
            amount = action.get("amount", 1.0)
            gathered = self.resources.gather_resource(
                agent.position[0],
                agent.position[1],
                resource_type,
                amount
            )
            
            if gathered > 0:
                self.log_event("resource_gathered", {
                    "agent_id": agent.id,
                    "resource": resource_type.value,
                    "amount": gathered
                })
                
        elif action["type"] == "discover":
            # Attempt to discover a technology
            tech_name = action["technology"]
            if self.technology.attempt_discovery(tech_name, agent.genes.get("intelligence", 0.5)):
                self.log_event("technology_discovered", {
                    "agent_id": agent.id,
                    "technology": tech_name
                })
                
        elif action["type"] == "process":
            # Process resources into new resources
            resource_type = ResourceType(action["resource"])
            amount = action.get("amount", 1.0)
            results = self.resources.process_resource(resource_type, amount)
            
            if results:
                self.log_event("resource_processed", {
                    "agent_id": agent.id,
                    "input": resource_type.value,
                    "outputs": {r.value: a for r, a in results.items()}
                })
                
        elif action["type"] == "mate":
            # Handle mating action
            target_id = action.get("target")
            if target_id and self.agents.get_agent(target_id):
                pregnancy = self.biology.initiate_pregnancy(agent.id, target_id)
                if pregnancy:
                    self.log_event("pregnancy_started", {
                        "mother_id": agent.id,
                        "father_id": target_id,
                        "due_date": pregnancy.due_date.isoformat()
                    })
                    
        elif action["type"] == "build":
            # Handle building construction
            settlement = None
            for group in self.society.social_groups.values():
                if agent.id in group.members:
                    for settlement_id in group.settlements:
                        if self.society.settlements[settlement_id].position == agent.position:
                            settlement = self.society.settlements[settlement_id]
                            break
                    if settlement:
                        break
                        
            if settlement:
                structure_type = action["structure"]
                if structure_type not in settlement.structures:
                    settlement.structures.append(structure_type)
                    self.log_event("structure_built", {
                        "agent_id": agent.id,
                        "settlement_id": settlement.id,
                        "structure": structure_type
                    })

    def remove_agent(self, agent_id: str):
        """Remove an agent from the world."""
        if self.agents.get_agent(agent_id):
            # Save final state before removal
            self.save_agent_data(agent_id)
            self.agents.agents.pop(agent_id, None)
            
        self.log_event("agent_death", {"agent_id": agent_id})

    def log_event(self, event_type: str, data: Dict):
        """Log an event in the world."""
        world_hours = (self.game_time - self.game_time_start).total_seconds() / 3600
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'world_time': world_hours,
            'data': data
        }
        self.events.append(event)
        logger.info(f"[{event['world_time']:.1f}h] {event_type}: {data}")
        
    def _add_event(self, agent_id: str, event_type: str, data: Dict):
        """Add an event for a specific agent."""
        agent = self.agents.get_agent(agent_id)
        if agent:
            event_data = {
                'agent_id': agent_id,
                'agent_name': agent.name,
                'description': data.get('description', ''),
                **data
            }
            self.log_event(event_type, event_data)
            
    def get_agent_json(self, agent_id: str) -> Dict:
        """Generate a comprehensive JSON representation of an agent's complete state."""
        if agent_id not in self.agents.agents:
            return {}
            
        agent = self.agents.agents[agent_id]
        
        # Get agent's social group
        social_group = None
        for group in self.society.social_groups.values():
            if agent_id in group.members:
                social_group = group
                break
        
        # Get agent's settlement
        settlement = None
        if social_group:
            for settlement_id in social_group.settlements:
                if agent_id in self.society.settlements[settlement_id].residents:
                    settlement = self.society.settlements[settlement_id]
                    break
        
        # Get agent's religion
        religion = None
        for rel in self.society.religions.values():
            if agent_id in rel.followers:
                religion = rel
                break
        
        # Get agent's recent memories and experiences
        recent_memories = [
            {
                "event": m.event,
                "importance": m.importance,
                "timestamp": m.timestamp.isoformat(),
                "context": m.context,
                "concepts": list(m.concepts),
                "animal_interactions": m.animal_interactions,
                "domesticated_animals": m.domesticated_animals,
                "emotional_impact": m.emotional_impact,
                "philosophical_impact": m.philosophical_impact,
                "cognitive_impact": m.cognitive_impact
            }
            for m in agent.get_recent_memories(10)  # Get last 10 memories
        ]
        
        # Get agent's current location and environment
        terrain = self.environment.get_terrain_at(*agent.position)
        climate = self.environment.get_climate_at(*agent.position)
        weather = self.environment.get_weather_at(*agent.position)
        
        # Build comprehensive JSON
        agent_json = {
            "basic_info": {
                "id": agent.id,
                "name": agent.name,
                "gender": agent.gender,
                "age": agent.age,
                "life_stage": agent.life_stage.value,
                "is_dead": agent.is_dead,
                "position": [float(agent.position[0]), float(agent.position[1])],
                "genes": agent.genes.__dict__
            },
            "physical_state": {
                "health": agent.health.to_dict(),
                "needs": agent.needs.__dict__,
                "diseases": agent.diseases,
                "injuries": agent.injuries,
                "strength": agent.genes.strength,
                "adaptability": agent.genes.adaptability
            },
            "mental_state": {
                "emotions": agent.emotions.to_dict(),
                "cognition": agent.cognition_state,
                "philosophy": agent.philosophy.to_dict(),
                "knowledge": agent.knowledge,
                "discovered_concepts": list(agent.discovered_concepts),
                "understanding_levels": agent.understanding_levels,
                "hypotheses": agent.hypotheses,
                "moral_alignment": agent.moral_alignment.value
            },
            "social_state": {
                "social_roles": agent.social_roles,
                "customs": agent.customs,
                "relationships": agent.relationships,
                "enemies": list(agent.enemies),
                "allies": list(agent.allies),
                "crimes_committed": agent.crimes_committed,
                "social_state": agent.social_state.__dict__,
                "crisis_state": agent.crisis_state.__dict__
            },
            "family": {
                "parents": agent.parents,
                "children": agent.children,
                "mate": agent.mate
            },
            "culture": {
                "social_group": {
                    "id": social_group.id if social_group else None,
                    "name": social_group.name if social_group else None,
                    "culture": social_group.culture if social_group else None,
                    "language_development": social_group.language_development if social_group else None
                },
                "settlement": {
                    "id": settlement.id if settlement else None,
                    "type": settlement.type if settlement else None,
                    "structures": settlement.structures if settlement else None
                },
                "religion": {
                    "name": religion.name if religion else None,
                    "beliefs": religion.beliefs if religion else None,
                    "practices": religion.practices if religion else None
                }
            },
            "skills_and_abilities": {
                "tools": agent.tools,
                "techniques": agent.techniques,
                "remedies": agent.remedies,
                "intelligence": agent.genes.intelligence,
                "creativity": agent.genes.creativity,
                "curiosity": agent.genes.curiosity,
                "social_drive": agent.genes.social_drive
            },
            "inventory": agent.inventory,
            "environment": {
                "terrain": terrain.type.value if terrain else "unknown",
                "climate": climate.get("terrain_type", "unknown"),
                "weather": weather.get("type", "unknown").value,
                "resources": {f"{lon},{lat}": resources for (lon, lat), resources in self.resources.get_resources_at(agent.position).items()}
            },
            "memories_and_experiences": {
                "recent_memories": recent_memories,
                "animal_interactions": agent.animal_interactions,
                "domesticated_animals": agent.domesticated_animals
            },
            "cognition_state": self.cognition_systems.get(agent_id, {}).get_state() if self.cognition_systems.get(agent_id) else None
        }
        
        return agent_json

    def _get_animal_state(self, animal: Animal) -> Dict:
        """Get current state of animal for the frontend."""
        return {
            "id": animal.id,
            "species": animal.species,
            "position": [float(animal.position[0]), float(animal.position[1])],
            "age": animal.age,
            "life_stage": animal.life_stage.value,
            "genes": animal.genes,
            "needs": animal.needs,
            "health": animal.health,
            "diseases": animal.diseases,
            "injuries": animal.injuries,
            "strength": animal.strength,
            "adaptability": animal.adaptability,
            "temperament": animal.temperament,
            "social_behavior": animal.social_behavior,
            "territorial_behavior": animal.territorial_behavior,
            "migration_pattern": animal.migration_pattern,
            "hunting_behavior": animal.hunting_behavior,
            "reproduction_behavior": animal.reproduction_behavior,
            "pack": animal.pack,
            "hierarchy": animal.hierarchy,
            "relationships": animal.relationships,
            "enemies": animal.enemies,
            "allies": animal.allies,
            "parents": animal.parents,
            "offspring": animal.offspring,
            "mate": animal.mate,
            "environment": {
                "terrain_type": animal.environment.terrain_type.value,
                "resources": {f"{k[0]},{k[1]}": v for k, v in animal.environment.resources.items()},
                "climate": animal.environment.climate.value,
                "weather": animal.environment.weather.value
            }
        }

    def get_state_for_agent(self, agent: Agent) -> Dict:
        """Get world state relevant to a specific agent."""
        return {
            "environment": self.environment.get_state(),
            "resources": self.resources.get_state(),
            "agents": {str(aid): a.get_state() for aid, a in self.agents.agents.items() if aid != agent.id},
            "animals": {str(animal.id): animal.get_state() for animal in self.animals.animals.values()},
            "time": self.game_time.isoformat(),
            "world_size": (self.environment.width, self.environment.height),
            "explored_area": self._get_explored_area(agent.position),
            "nearby_resources": {f"{lon},{lat}": resources for (lon, lat), resources in self.environment.get_nearby_resources(*agent.position, radius=5).items()},
            "nearby_climate": {f"{lon},{lat}": climate for (lon, lat), climate in self.environment.get_nearby_climate(*agent.position, radius=5).items()},
            "weather": self.environment.get_weather_at(*agent.position),
            "climate": self.environment.get_climate_at(*agent.position),
            "terrain": self.environment.get_terrain_at(*agent.position)
        }

    def calculate_distance(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """Calculate distance between two points using the Haversine formula."""
        return self.get_distance(lon1, lat1, lon2, lat2)

    def can_travel_between(self, start_lon: float, start_lat: float, end_lon: float, end_lat: float, transport_type: TransportationType) -> bool:
        """Check if travel is possible between two points using the given transport type."""
        # Get terrain at both points
        start_terrain = self.get_terrain_at(start_lon, start_lat)
        end_terrain = self.get_terrain_at(end_lon, end_lat)
        
        # Get weather conditions
        start_weather = self.get_weather_at(start_lon, start_lat)
        end_weather = self.get_weather_at(end_lon, end_lat)
        
        # Check if transport type is valid for terrain
        if transport_type == TransportationType.LAND:
            return (start_terrain != TerrainType.WATER and 
                   end_terrain != TerrainType.WATER)
        elif transport_type == TransportationType.WATER:
            return (start_terrain == TerrainType.WATER and 
                   end_terrain == TerrainType.WATER)
        elif transport_type == TransportationType.AIR:
            # Air travel is possible in most conditions except severe storms
            return (start_weather["type"] not in [WeatherType.STORM, WeatherType.HURRICANE] and
                   end_weather["type"] not in [WeatherType.STORM, WeatherType.HURRICANE])
        
        return False

    def calculate_travel_time(self, start_lon: float, start_lat: float, end_lon: float, end_lat: float, transport_type: TransportationType) -> timedelta:
        """Calculate travel time between two points using the given transport type."""
        # Calculate distance
        distance = self.calculate_distance(start_lon, start_lat, end_lon, end_lat)
        
        # Get average speed for transport type (km/h)
        speeds = {
            TransportationType.LAND: 5.0,  # Walking speed
            TransportationType.WATER: 10.0,  # Sailing speed
            TransportationType.AIR: 100.0  # Flying speed
        }
        
        speed = speeds.get(transport_type, 5.0)
        
        # Calculate time in hours
        hours = distance / speed
        
        return timedelta(hours=hours)

    def get_travel_options(self, start_lon: float, start_lat: float, end_lon: float, end_lat: float) -> List[Tuple[TransportationType, timedelta]]:
        """Get all possible travel options between two points."""
        options = []
        
        for transport_type in TransportationType:
            if self.can_travel_between(start_lon, start_lat, end_lon, end_lat, transport_type):
                travel_time = self.calculate_travel_time(start_lon, start_lat, end_lon, end_lat, transport_type)
                options.append((transport_type, travel_time))
                
        return options

    def get_nearest_land(self, lon: float, lat: float) -> Optional[Tuple[float, float]]:
        """Find the nearest land point to the given coordinates."""
        if self.get_terrain_at(lon, lat) != TerrainType.WATER:
            return (lon, lat)
            
        # Search in expanding circles
        search_radius = 0.1  # Start with 0.1 degrees
        max_radius = 1.0  # Maximum search radius
        
        while search_radius <= max_radius:
            # Calculate bounds
            min_lon = max(self.min_longitude, lon - search_radius)
            max_lon = min(self.max_longitude, lon + search_radius)
            min_lat = max(self.min_latitude, lat - search_radius)
            max_lat = min(self.max_latitude, lat + search_radius)
            
            # Check each point in the area
            for test_lon in np.arange(min_lon, max_lon, self.longitude_resolution):
                for test_lat in np.arange(min_lat, max_lat, self.latitude_resolution):
                    # Check if point is within radius
                    if self.get_distance(lon, lat, test_lon, test_lat) <= search_radius:
                        if self.get_terrain_at(test_lon, test_lat) != TerrainType.WATER:
                            return (test_lon, test_lat)
                            
            search_radius += 0.1
            
        return None

    def get_environment_state(self) -> Dict:
        """Get current environment state."""
        return {
            "width": self.width,
            "height": self.height,
            "terrain": self.terrain.get_state(),
            "climate": self.climate.get_state(),
            "weather": self.weather.get_state(),
            "resources": self.resources.get_state(),
            "marine": self.marine.get_state()
        }

    def load_agent_data(self):
        """Load existing agent data from JSON files."""
        for filename in os.listdir(self.db_dir):
            if filename.endswith('.json'):
                agent_id = filename[:-5]  # Remove .json extension
                try:
                    with open(os.path.join(self.db_dir, filename), 'r') as f:
                        data = json.load(f)
                        agent = self.agents.get_agent(agent_id)
                        if agent:
                            agent.update_from_save(data)
                except Exception as e:
                    logger.error(f"Error loading agent data for {agent_id}: {str(e)}")
                    
    def save_agent_data(self, agent_id: str = None):
        """Save agent data to JSON files."""
        if agent_id:
            # Save single agent
            agent = self.agents.get_agent(agent_id)
            if not agent:
                return
            agents_to_save = {agent_id: agent}
        else:
            # Save all agents
            agents_to_save = self.agents.agents
            
        # Ensure agents directory exists
        agents_dir = os.path.join(self.db_dir, "agents")
        os.makedirs(agents_dir, exist_ok=True)
            
        for aid, agent in agents_to_save.items():
            try:
                data = agent.to_dict()
                data['last_saved'] = datetime.now().isoformat()
                
                with open(os.path.join(agents_dir, f"{aid}.json"), 'w') as f:
                    json.dump(data, f, indent=2)
                    
                logger.info(f"Saved data for agent {agent.name} ({aid})")
            except Exception as e:
                logger.error(f"Error saving agent data for {aid}: {str(e)}")

    def get_marine_creature_json(self, creature_id: str) -> Dict:
        """Get JSON representation of a marine creature."""
        if creature_id not in self.marine.creatures:
            return None
        
        creature = self.marine.creatures[creature_id]
        return {
            "id": creature_id,
            "species": creature.species,
            "age": creature.age,
            "health": creature.health,
            "longitude": creature.longitude,
            "latitude": creature.latitude,
            "size": creature.size,
            "diet": creature.diet,
            "reproduction_status": creature.reproduction_status,
            "last_updated": creature.last_updated.isoformat() if creature.last_updated else None
        }

    def __getstate__(self):
        """Prepare object for serialization."""
        return {
            'terrain': self.terrain,
            'climate': self.climate,
            'marine': self.marine,
            'min_longitude': self.min_longitude,
            'max_longitude': self.max_longitude,
            'min_latitude': self.min_latitude,
            'max_latitude': self.max_latitude,
            'longitude_resolution': self.longitude_resolution,
            'latitude_resolution': self.latitude_resolution
        }
        
    def __setstate__(self, state):
        """Restore object from serialization."""
        self.terrain = state['terrain']
        self.climate = state['climate']
        self.marine = state['marine']
        self.min_longitude = state['min_longitude']
        self.max_longitude = state['max_longitude']
        self.min_latitude = state['min_latitude']
        self.max_latitude = state['max_latitude']
        self.longitude_resolution = state['longitude_resolution']
        self.latitude_resolution = state['latitude_resolution']
        
        # Restore world references
        self.terrain.world = self
        self.climate.world = self
        self.marine.world = self

    def get_regions(self) -> List[Dict]:
        """Get all regions in the world for animal initialization.
        Each region is a dictionary containing:
        - center: (longitude, latitude) tuple
        - terrain_type: string describing the terrain
        - size: approximate size in square kilometers
        """
        regions = []
        
        # Create regions based on terrain types
        for lon in range(-180, 181, 5):  # Every 5 degrees
            for lat in range(-90, 91, 5):
                terrain = self.terrain.get_terrain_at(lon, lat)
                if terrain and terrain != "void":  # Check if terrain exists and is not void
                    regions.append({
                        "center": [float(lon), float(lat)],
                        "terrain_type": terrain.value if hasattr(terrain, 'value') else terrain,  # Handle both enum and string
                        "size": 5000  # Approximate size in square kilometers
                    })
        
        return regions

    def _save_state(self):
        """Save the current world state to disk."""
        try:
            # Ensure save directory exists
            save_dir = os.path.join('simulation_saves', 'current_world')
            os.makedirs(save_dir, exist_ok=True)
            
            # Save world state
            world_state = {
                'current_tick': self.current_tick,
                'game_time': self.game_time.isoformat(),
                'simulation_time': self.simulation_time,
                'day': self.day,
                'year': self.year,
                'events': self.events[-100:]  # Keep last 100 events
            }
            
            # Save world state
            with open(os.path.join(save_dir, 'world_state.json'), 'w') as f:
                json.dump(world_state, f, indent=2)
            
            # Save agent states
            agent_states = {}
            for agent_id, agent in self.agents.agents.items():
                agent_states[str(agent_id)] = {
                    'id': agent.id,
                    'name': agent.name,
                    'position': agent.position,
                    'health': agent.health,
                    'energy': agent.energy,
                    'hunger': agent.hunger,
                    'thirst': agent.thirst,
                    'age': agent.age,
                    'skills': agent.skills,
                    'inventory': agent.inventory,
                    'last_action': agent.last_action
                }
            
            with open(os.path.join(save_dir, 'agents.json'), 'w') as f:
                json.dump(agent_states, f, indent=2)
            
            self.logger.info(f"Saved world state at tick {self.current_tick}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving world state: {e}")
            self.logger.error(traceback.format_exc())
            return False

    def _load_state(self):
        """Load the most recent world state from disk."""
        try:
            logger.info("[LOAD] Attempting to load world state...")
            saves_dir = 'simulation_saves'
            
            # Check if saves directory exists
            if not os.path.exists(saves_dir):
                logger.info("[LOAD] No simulation_saves directory found.")
                return False
            
            # Get all save directories
            saves = [d for d in os.listdir(saves_dir) if d.startswith('world_state_')]
            if not saves:
                logger.info("[LOAD] No world_state_ saves found.")
                return False
            
            # Get the latest save directory
            latest_save = max(saves)
            save_dir = os.path.join(saves_dir, latest_save)
            
            # Check if the save directory exists and has required files
            if not os.path.exists(save_dir):
                logger.info(f"[LOAD] Save directory {save_dir} does not exist.")
                return False
                
                return False
                
            logger.info(f"[LOAD] Loading from directory: {save_dir}")
            
            # Load metadata
            with open(os.path.join(save_dir, 'metadata.json'), 'r') as f:
                metadata = json.load(f)
            logger.info(f"[LOAD] Loaded metadata: {metadata}")
            
            # Load each system's state
            systems = {
                'terrain': self.terrain,
                'climate': self.climate,
                'resources': self.resources,
                'plants': self.plants,
                'animals': self.animals,
                'marine': self.marine,
                'technology': self.technology,
                'society': self.society,
                'transportation': self.transportation
            }
            
            for name, system in systems.items():
                state_file = os.path.join(save_dir, f'{name}.json')
                if os.path.exists(state_file):
                    try:
                        with open(state_file, 'r') as f:
                            state = json.load(f)
                        if hasattr(system, 'load_state'):
                            system.load_state(state)
                        else:
                            # For simple attributes, update directly
                            for key, value in state.items():
                                setattr(system, key, value)
                        logger.info(f"[LOAD] Loaded {name} state from {state_file}")
                    except Exception as sys_e:
                        logger.error(f"[LOAD] Error loading {name}: {sys_e}")
                else:
                    logger.warning(f"[LOAD] State file missing for {name}: {state_file}")
            
            logger.info(f"[LOAD] Successfully loaded world state from {save_dir}")
            return True
            
        except Exception as e:
            logger.error(f"[LOAD] Error loading world state: {str(e)}")
            return False

    def _get_plant_state(self, plant: Plant) -> Dict:
        """Get current state of plant for the frontend."""
        return {
            "id": plant.id,
            "type": plant.type.value,
            "species": plant.species,
            "position": [float(plant.position[0]), float(plant.position[1])],
            "age": plant.age,
            "health": plant.health,
            "size": plant.size,
            "growth_rate": plant.growth_rate,
            "reproduction_rate": plant.reproduction_rate,
            "spread_rate": plant.spread_rate,
            "biomass": plant.biomass,
            "carbon_sequestration": plant.carbon_sequestration,
            "oxygen_production": plant.oxygen_production,
            "soil_stabilization": plant.soil_stabilization,
            "habitat_value": plant.habitat_value,
            "resource_production": plant.resource_production,
            "environment": {
                "terrain_type": plant.environment.terrain_type.value,
                "resources": {f"{k[0]},{k[1]}": v for k, v in plant.environment.resources.items()},
                "climate": plant.environment.climate.value,
                "weather": plant.environment.weather.value
            }
        }

    def _get_marine_state(self, marine: Marine) -> Dict:
        """Get current state of marine for the frontend."""
        return {
            "id": marine.id,
            "type": marine.type.value,
            "species": marine.species,
            "position": [float(marine.position[0]), float(marine.position[1])],
            "age": marine.age,
            "health": marine.health,
            "size": marine.size,
            "growth_rate": marine.growth_rate,
            "reproduction_rate": marine.reproduction_rate,
            "spread_rate": marine.spread_rate,
            "biomass": marine.biomass,
            "carbon_sequestration": marine.carbon_sequestration,
            "oxygen_production": marine.oxygen_production,
            "habitat_value": marine.habitat_value,
            "resource_production": marine.resource_production,
            "environment": {
                "terrain_type": marine.environment['terrain_type'],
                "resources": marine.environment['resources'],
                "climate": marine.environment['climate'],
                "weather": marine.environment['weather']
            }
        }

    def _get_weather_state(self, weather: WeatherState) -> Dict:
        """Get current state of weather for the frontend."""
        return {
            "type": weather.type.value,
            "temperature": weather.temperature,
            "humidity": weather.humidity,
            "wind_speed": weather.wind_speed,
            "wind_direction": weather.wind_direction,
            "precipitation": weather.precipitation,
            "cloud_cover": weather.cloud_cover,
            "air_pressure": weather.air_pressure,
            "visibility": weather.visibility,
            "position": [float(weather.position[0]), float(weather.position[1])]
        }

    def _get_climate_state(self, climate: ClimateType) -> Dict:
        """Get current state of climate for the frontend."""
        return {
            "type": climate.value,
            "temperature": self.climate.temperature,
            "humidity": self.climate.humidity,
            "precipitation": self.climate.precipitation,
            "wind_speed": self.climate.wind_speed,
            "wind_direction": self.climate.wind_direction,
            "air_pressure": self.climate.air_pressure,
            "visibility": self.climate.visibility,
            "position": [float(self.climate.position[0]), float(self.climate.position[1])]
        }

    def _get_terrain_state(self, terrain: TerrainType) -> Dict:
        """Get current state of terrain for the frontend."""
        return {
            "type": terrain.value,
            "elevation": self.terrain.get_elevation_at(terrain.position[0], terrain.position[1]),
            "slope": self.terrain.get_slope_at(terrain.position[0], terrain.position[1]),
            "roughness": self.terrain.get_roughness_at(terrain.position[0], terrain.position[1]),
            "fertility": self.terrain.get_fertility_at(terrain.position[0], terrain.position[1]),
            "water_content": self.terrain.get_water_content_at(terrain.position[0], terrain.position[1]),
            "mineral_content": self.terrain.get_mineral_content_at(terrain.position[0], terrain.position[1]),
            "vegetation_cover": self.terrain.get_vegetation_cover_at(terrain.position[0], terrain.position[1]),
            "position": [float(terrain.position[0]), float(terrain.position[1])]
        }

    def _get_resource_state(self, resource: Resource) -> Dict:
        """Get current state of resource for the frontend."""
        return {
            "type": resource.type.value,
            "amount": resource.amount,
            "quality": resource.quality,
            "position": [float(resource.position[0]), float(resource.position[1])]
        }

    def _get_society_state(self, society: Society) -> Dict:
        """Get current state of society for the frontend."""
        return {
            "name": society.name,
            "type": society.type.value,
            "population": society.population,
            "culture": society.culture,
            "language": society.language,
            "religion": society.religion,
            "technology": society.technology,
            "resources": {f"{k[0]},{k[1]}": v for k, v in society.resources.items()},
            "settlements": {f"{k[0]},{k[1]}": v for k, v in society.settlements.items()},
            "territories": {f"{k[0]},{k[1]}": v for k, v in society.territories.items()},
            "relationships": society.relationships,
            "conflicts": society.conflicts,
            "alliances": society.alliances,
            "treaties": society.treaties,
            "position": [float(society.position[0]), float(society.position[1])]
        }

    def _get_transportation_state(self, transportation: TransportationType) -> Dict:
        """Get current state of transportation for the frontend."""
        return {
            "type": transportation.value,
            "routes": {f"{k[0]},{k[1]}": v for k, v in self.transportation.routes.items()},
            "capacity": self.transportation.capacity,
            "speed": self.transportation.speed,
            "efficiency": self.transportation.efficiency,
            "cost": self.transportation.cost,
            "position": [float(self.transportation.position[0]), float(self.transportation.position[1])]
        }

    def _get_technology_state(self, technology: Technology) -> Dict:
        """Get current state of technology for the frontend."""
        return {
            "type": technology.type.value,
            "level": technology.level,
            "progress": technology.progress,
            "requirements": technology.requirements,
            "effects": technology.effects,
            "position": [float(technology.position[0]), float(technology.position[1])]
        }

    def _get_discovery_state(self, discovery: Discovery) -> Dict:
        """Get current state of discovery for the frontend."""
        return {
            "type": discovery.type.value,
            "progress": discovery.progress,
            "requirements": discovery.requirements,
            "effects": discovery.effects,
            "position": [float(discovery.position[0]), float(discovery.position[1])]
        }

    def _get_environment_state(self, environment: Environment) -> Dict:
        """Get current state of environment for the frontend."""
        return {
            "type": environment.type,
            "name": environment.name,
            "description": environment.description,
            "temperature": environment.temperature,
            "humidity": environment.humidity,
            "precipitation": environment.precipitation,
            "wind_speed": environment.wind_speed,
            "wind_direction": environment.wind_direction,
            "pressure": environment.pressure,
            "visibility": environment.visibility,
            "center_longitude": environment.center_longitude,
            "center_latitude": environment.center_latitude,
            "time_of_day": environment.time_of_day,
            "season": environment.season,
            "current_time": self.game_time.isoformat(),
        }
