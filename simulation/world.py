from typing import Dict, List, Optional, Tuple, Set
import random
import uuid
from datetime import datetime, timedelta
from .agent import Agent, Genes
from .environment import Environment, TerrainType
from .llm import AgentCognition
from .biology import Biology
from .technology import TechnologyTree
from .resources import ResourceSystem, ResourceType
from .society import Society, SocialStructure, Culture, Settlement
from .discovery import DiscoverySystem, Discovery
from .animals import AnimalSystem
from .life_cycle import LifeCycleSystem
from .philosophy import Philosophy
from .emotions import EmotionSystem
from .health import Health
from .relationships import Relationships
from .economy import Economy
import logging
import math
from .transportation import TransportationSystem, TransportationType
from .weather import WeatherSystem, WeatherType, WeatherState
from .marine import MarineSystem
from .climate import ClimateType
from .terrain import OceanCurrent
from simulation.terrain import TerrainSystem
from simulation.climate import ClimateSystem
from simulation.plants import PlantSystem
import json
import os
from .genes import Genes
from .needs import AgentNeeds
from .memory import Memory
from .technology import TechnologySystem
from .society import SocietySystem

logger = logging.getLogger(__name__)

class World:
    def __init__(self, world_size: int = 1000):
        logger.info("Creating new world...")
        # Earth's dimensions
        self.min_longitude = -180
        self.max_longitude = 180
        self.min_latitude = -90
        self.max_latitude = 90
        
        # Earth's dimensions
        self.EARTH_CIRCUMFERENCE = 40075  # km
        self.EARTH_RADIUS = 6371  # km
        # Grid resolution (1 degree = ~111km at equator)
        self.longitude_resolution = 0.1  # degrees
        self.latitude_resolution = 0.1  # degrees
        
        self.world_size = world_size
        self.terrain = TerrainSystem(self)
        self.climate = ClimateSystem(self)
        self.resources = ResourceSystem(self)
        self.plants = PlantSystem(world_size, self)
        self.animals = AnimalSystem(world_size)
        self.marine = MarineSystem(self)
        self.transportation = TransportationSystem(world_size)
        self.weather = WeatherSystem(world_size)
        self.discovery = DiscoverySystem(world_size)
        self.cognitive = CognitiveSystem(world_size)
        self.civilization = CivilizationSystem(world_size)
        
        # Initialize state
        self.current_tick = 0
        self.simulation_time = 0.0
        self.explored_areas = set()
        self.discoveries = []
        self.events = []
        
        # Initialize environment first
        self.environment = Environment()
        
        # Initialize systems using real-world coordinates
        self.transportation_system = TransportationSystem(self)
        
        # Time tracking
        self.real_time_start = datetime.now()
        self.game_time_start = datetime(1000, 1, 1)  # Start in year 1000
        self.time_scale = 1.0  # 1 real second = 1 game hour
        
        # Initialize other systems
        self.agents: Dict[str, Agent] = {}
        self.settlements: Dict[str, Settlement] = {}
        self.cultures: Dict[str, Culture] = {}
        self.life_cycle_system = LifeCycleSystem()
        
        # Initialize database directory
        self.db_dir = "agent_data"
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
            
        # Load existing agent data if any
        self.load_agent_data()
        
        # Initialize world state
        self._initialize_world()
        
        logger.info("World created successfully")
        
    def _initialize_world(self):
        """Initialize the world state."""
        # Generate terrain
        self.terrain.initialize_terrain()
        
        # Initialize climate
        self.climate.initialize_earth_climate()
        
        # Initialize weather
        self.weather.initialize_weather_systems()
        
        # Initialize resources
        self.resources.initialize_resources()
        
        # Initialize transportation
        self.transportation_system.initialize_transportation()
        
        # Initialize ocean systems
        self.terrain.initialize_ocean_systems()
        
        # Create initial settlements
        self._create_initial_settlements()
        
        # Create initial agents
        self._create_initial_agents()
        
        # Spawn initial marine life
        self.marine.spawn_creatures(count=1000)
        
    def _create_initial_settlements(self):
        """Create initial settlements in the world."""
        # Create a few major settlements
        settlements = [
            {
                "name": "New York",
                "longitude": -74.0060,
                "latitude": 40.7128,
                "population": 1000,
                "culture": "American"
            },
            {
                "name": "London",
                "longitude": -0.1278,
                "latitude": 51.5074,
                "population": 800,
                "culture": "British"
            },
            {
                "name": "Tokyo",
                "longitude": 139.6917,
                "latitude": 35.6895,
                "population": 900,
                "culture": "Japanese"
            }
        ]
        
        for settlement_data in settlements:
            settlement_id = str(uuid.uuid4())
            self.settlements[settlement_id] = Settlement(
                id=settlement_id,
                name=settlement_data["name"],
                longitude=settlement_data["longitude"],
                latitude=settlement_data["latitude"],
                population=settlement_data["population"],
                culture=settlement_data["culture"]
            )
            
    def _create_initial_agents(self):
        """Create initial agents (Adam and Eve)"""
        logger.info("Creating initial agents (Adam and Eve)...")
        
        # Create Adam (Avi)
        adam = Agent(
            id="adam",
            name="Avi",
            last_name="Taub",
            age=25.0,
            gender="male",
            genes=Genes(),
            needs=AgentNeeds(),
            memory=Memory(),
            emotions=EmotionSystem(),
            health=1.0,
            philosophy=Philosophy(),
            longitude=0.0,
            latitude=0.0
        )
        
        # Create Eve (Yehudit)
        eve = Agent(
            id="eve",
            name="Yehudit",
            last_name="Taub",
            age=25.0,
            gender="female",
            genes=Genes(),
            needs=AgentNeeds(),
            memory=Memory(),
            emotions=EmotionSystem(),
            health=1.0,
            philosophy=Philosophy(),
            longitude=0.1,
            latitude=0.1
        )
        
        self.agents["adam"] = adam
        self.agents["eve"] = eve
        logger.info("Initial agents created")
        
    def update(self, time_scale=1.0):
        """Update the world state"""
        self.current_tick += 1
        self.simulation_time += time_scale
        
        # Update systems
        self.terrain.update()
        self.climate.update()
        self.animals.update(self)
        
        # Update agents
        for agent_id, agent in list(self.agents.items()):
            try:
                agent.update(self)
                logger.debug(f"Updated agent {agent.name} (ID: {agent_id})")
            except Exception as e:
                logger.error(f"Error updating agent {agent_id}: {str(e)}", exc_info=True)
        
        # Update civilization systems
        self.technology.update(self)
        self.society.update(self)
        
        # Log major events every 100 ticks
        if self.current_tick % 100 == 0:
            self._log_world_state()
        
    def _log_world_state(self):
        """Log the current state of the world"""
        logger.info(f"World State at tick {self.current_tick}:")
        logger.info(f"  Simulation time: {self.simulation_time:.2f} hours")
        logger.info(f"  Agents: {len(self.agents)}")
        logger.info(f"  Animals: {len(self.animals.animals)}")
        logger.info(f"  Inventions: {len(self.technology.discoveries)}")
        logger.info(f"  Religions: {len(self.society.religions)}")
        logger.info(f"  Languages: {len(self.society.languages)}")
        
        # Log agent details
        for agent_id, agent in self.agents.items():
            logger.info(f"  Agent {agent.name} (ID: {agent_id}):")
            logger.info(f"    Age: {agent.age:.1f}, Health: {agent.health:.2f}")
            logger.info(f"    Position: ({agent.longitude:.2f}, {agent.latitude:.2f})")
            logger.info(f"    Needs - Food: {agent.needs.food:.2f}, Water: {agent.needs.water:.2f}")
        
    def get_state(self):
        """Get the current state of the world"""
        return {
            "tick": self.current_tick,
            "simulation_time": self.simulation_time,
            "agents": {id: agent.to_dict() for id, agent in self.agents.items()},
            "animals": self.animals.get_state(),
            "terrain": self.terrain.get_state(),
            "climate": self.climate.get_state(),
            "technology": self.technology.get_state(),
            "society": self.society.get_state()
        }
        
    def get_world_state(self) -> Dict:
        """Get current world state for agents."""
        return {
            "time": self.game_time,
            "terrain": self.terrain.get_state(),
            "climate": self.climate.get_state(),
            "weather": self.weather.get_state(),
            "resources": self.resources.get_state(),
            "transportation": self.transportation_system.get_state(),
            "settlements": {id: settlement.get_state() for id, settlement in self.settlements.items()},
            "agents": {id: agent.get_state() for id, agent in self.agents.items()},
            "marine": self.marine.get_state(),
            "environmental_conditions": {
                "temperature": self.climate.get_temperature_at,
                "salinity": self.terrain.get_salinity_at,
                "oxygen": self.terrain.get_oxygen_at,
                "current": self.terrain.get_current_at,
                "depth": self.terrain.get_depth_at,
                "tidal_range": self.terrain.get_tidal_range_at
            }
        }
        
    def get_terrain_at(self, longitude: float, latitude: float) -> TerrainType:
        """Get terrain type at given coordinates."""
        return self.terrain.get_terrain_at(longitude, latitude)
        
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
                
    def get_spawn_location(self) -> Tuple[float, float]:
        """Get a random spawn location within the initial spawn area."""
        center_lon = self.initial_spawn["longitude"]
        center_lat = self.initial_spawn["latitude"]
        radius = self.initial_spawn["radius"]
        
        # Generate random point within radius
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius)
        
        # Convert to longitude/latitude
        lon = center_lon + (distance * math.cos(angle))
        lat = center_lat + (distance * math.sin(angle))
        
        return (lon, lat)

    def get_current_game_time(self) -> datetime:
        """Convert real time to game time."""
        real_time_elapsed = datetime.now() - self.real_time_start
        game_time_elapsed = timedelta(hours=real_time_elapsed.total_seconds() * self.time_scale)
        return self.game_time_start + game_time_elapsed

    def get_distance(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """Calculate distance between two points using the Haversine formula."""
        # Convert to radians
        lat1, lon1 = math.radians(lat1), math.radians(lon1)
        lat2, lon2 = math.radians(lat2), math.radians(lon2)
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = self.EARTH_RADIUS * c  # Earth's radius in km
        
        return distance

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

    def spawn_initial_agents(self, count: int = 2):
        """Spawn initial agents in the world."""
        agent_ids = []
        positions = []
        
        logger.info(f"Spawning {count} initial agents...")
        
        # First two agents are Adam and Eve
        first_names = ["Adam", "Eve"]
        first_genders = ["male", "female"]
        
        for i in range(count):
            # Find a suitable spawn location (not water)
            while True:
                x = random.randint(0, self.environment.width - 1)
                y = random.randint(0, self.environment.height - 1)
                if self.environment.get_terrain_at(x, y).type.value != "water":
                    break

            # Create agent
            agent_id = f"agent_{i}"
            genes = Genes(
                curiosity=random.random(),
                strength=random.random(),
                intelligence=random.random(),
                social_drive=random.random(),
                creativity=random.random(),
                adaptability=random.random()
            )
            
            # Use Adam/Eve for first two agents
            if i < 2:
                name = first_names[i]
                gender = first_genders[i]
            else:
                name = self._generate_name()[0]
                gender = random.choice(["male", "female"])
            
            # Initialize cognition system first
            cognition = AgentCognition(agent_id)
            self.cognition_systems[agent_id] = cognition
            
            # Create agent with the cognition system
            agent = Agent(
                id=agent_id,
                name=name,
                position=(x, y),
                genes=genes,
                gender=gender
            )
            
            # Initialize agent's cognition state
            agent.cognition_state = cognition.get_state()
            
            self.agents[agent_id] = agent
            
            # Generate initial resources at agent's location
            terrain = self.environment.get_terrain_at(x, y)
            self.resources.generate_resources(x, y, terrain.type.value)
            
            agent_ids.append(agent_id)
            positions.append((x, y))
            
            logger.info(f"Created agent {agent.name} (ID: {agent_id}) at position {x}, {y}")
            self.log_event("agent_spawn", {
                "agent_id": agent_id,
                "name": agent.name,
                "gender": gender,
                "position": (x, y),
                "genes": genes.__dict__,
                "cognition_state": cognition.get_state()
            })
            
        # Create initial society
        self.society.create_initial_society(agent_ids, positions)
        logger.info(f"Created initial society with {len(agent_ids)} agents")

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

    def _spawn_child(self, child):
        """Spawn a new child agent."""
        # Find a suitable spawn location near the mother
        mother = self.agents[child.mother_id]
        father = self.agents[child.father_id]
        x, y = mother.position
        
        # Try to find a nearby empty spot
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = x + dx
            new_y = y + dy
            if (0 <= new_x < self.environment.width and 
                0 <= new_y < self.environment.height and
                self.environment.get_terrain_at(new_x, new_y).type.value != "water"):
                break
        else:
            # If no nearby spot, use mother's position
            new_x, new_y = x, y

        # Generate name based on parents' culture and language
        first_name, last_name = self._generate_child_name(mother, father)
        
        # Initialize cognition system first
        cognition = AgentCognition(child.id)
        self.cognition_systems[child.id] = cognition
        
        # Create new agent
        agent = Agent(
            id=child.id,
            name=f"{first_name} {last_name}",
            position=(new_x, new_y),
            genes=child.genes,
            gender=child.gender
        )
        
        self.agents[child.id] = agent
        
        self.log_event("child_birth", {
            "child_id": child.id,
            "name": f"{first_name} {last_name}",
            "mother_id": child.mother_id,
            "father_id": child.father_id,
            "position": (new_x, new_y)
        })

    def _get_agent_state(self, agent: Agent) -> Dict:
        """Get current state of an agent for the frontend."""
        # Get resources at agent's position
        resources = self.resources.get_resources_at(agent.position)
        
        # Get recent memories
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
            for m in agent.get_recent_memories(5)
        ]
        
        # Get terrain at agent's position
        terrain = self.environment.get_terrain_at(*agent.position)
        
        return {
            "id": agent.id,
            "name": agent.name,
            "position": agent.position,
            "age": agent.age,
            "life_stage": agent.life_stage.value,
            "genes": agent.genes.__dict__,
            "needs": agent.needs.__dict__,
            "discovered_concepts": list(agent.discovered_concepts),
            "understanding_levels": agent.understanding_levels,
            "hypotheses": agent.hypotheses,
            "relationships": agent.relationships,
            "social_roles": agent.social_roles,
            "customs": agent.customs,
            "tools": agent.tools,
            "techniques": agent.techniques,
            "emotional_concepts": list(agent.emotional_concepts),
            "health_concepts": list(agent.health_concepts),
            "remedies": agent.remedies,
            "philosophy": agent.philosophy.to_dict(),
            "emotions": agent.emotions.to_dict(),
            "cognition": agent.cognition_state,
            "inventory": agent.inventory,
            "diseases": agent.diseases,
            "injuries": agent.injuries,
            "family": {
                "parents": agent.parents,
                "children": agent.children,
                "mate": agent.mate
            },
            "memory": {
                "recent_memories": recent_memories,
                "animal_interactions": agent.animal_interactions,
                "domesticated_animals": agent.domesticated_animals
            },
            "moral_alignment": agent.moral_alignment.value,
            "crisis_state": agent.crisis_state.__dict__,
            "crimes_committed": agent.crimes_committed,
            "enemies": list(agent.enemies),
            "allies": list(agent.allies),
            "social_state": agent.social_state.__dict__,
            "gender": agent.gender,
            "is_dead": agent.is_dead,
            "resources": resources,
            "terrain": terrain.type.value if terrain else "unknown",  # Access the type attribute first
            "climate": self.environment.get_climate_at(*agent.position).get("terrain_type", "unknown"),  # Get terrain_type from climate data
            "weather": self.environment.get_weather_at(*agent.position).get("type", "unknown").value  # Get weather type and its value
        }

    def _get_explored_area(self, longitude: float, latitude: float, radius: float = 0.1) -> List[Dict]:
        """Get all explored areas within radius degrees of the given coordinates."""
        explored_areas = []
        
        # Calculate bounds
        min_lon = max(self.min_longitude, longitude - radius)
        max_lon = min(self.max_longitude, longitude + radius)
        min_lat = max(self.min_latitude, latitude - radius)
        max_lat = min(self.max_latitude, latitude + radius)
        
        # Check each tile in the area
        for lon in range(int(min_lon / self.longitude_resolution), 
                        int(max_lon / self.longitude_resolution) + 1):
            for lat in range(int(min_lat / self.latitude_resolution),
                           int(max_lat / self.latitude_resolution) + 1):
                tile_lon = lon * self.longitude_resolution
                tile_lat = lat * self.latitude_resolution
                
                # Check if tile is within radius
                if self.get_distance(longitude, latitude, tile_lon, tile_lat) <= radius:
                    # Get terrain and resources
                    terrain = self.get_terrain_at(tile_lon, tile_lat)
                    resources = self.get_resources_at(tile_lon, tile_lat)
                    
                    explored_areas.append({
                        "longitude": tile_lon,
                        "latitude": tile_lat,
                        "terrain": terrain,
                        "resources": resources
                    })
                    
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
            self.explored_tiles.add((new_x, new_y))
            
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
            if target_id and target_id in self.agents:
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
        if agent_id in self.agents:
            # Save final state before removal
            self.save_agent_data(agent_id)
            del self.agents[agent_id]
            
        self.log_event("agent_death", {"agent_id": agent_id})

    def log_event(self, event_type: str, data: Dict):
        """Log an event in the world."""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'world_time': self.game_time.total_seconds() / 3600,  # Convert to hours
            'data': data
        }
        self.events.append(event)
        logger.info(f"[{event['world_time']:.1f}h] {event_type}: {data}")
        
    def _add_event(self, agent_id: str, event_type: str, data: Dict):
        """Add an event for a specific agent."""
        agent = self.agents.get(agent_id)
        if agent:
            event_data = {
                'agent_id': agent_id,
                'agent_name': agent.name,
                'description': data.get('description', ''),
                **data
            }
            self.log_event(event_type, event_data)
            
    def to_dict(self) -> Dict:
        """Convert world state to dictionary for serialization."""
        return {
            "game_time": self.game_time,
            "day": self.day,
            "year": self.year,
            "environment": self.environment.to_dict(),
            "agents": {
                agent_id: agent.to_dict()
                for agent_id, agent in self.agents.items()
            },
            "biology": self.biology.to_dict(),
            "technology": self.technology.to_dict(),
            "resources": self.resources.to_dict(),
            "society": self.society.to_dict(),
            "explored_tiles": list(self.explored_tiles),
            "events": self.events[-100:],  # Keep last 100 events
            "discovery": self.discovery.to_dict()
        }

    def get_agent_json(self, agent_id: str) -> Dict:
        """Generate a comprehensive JSON representation of an agent's complete state."""
        if agent_id not in self.agents:
            return {}
            
        agent = self.agents[agent_id]
        cognition = self.cognition_systems[agent_id]
        
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
                "position": agent.position,
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
                    "name": settlement.name if settlement else None,
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
                "resources": self.resources.get_resources_at(agent.position)
            },
            "memories_and_experiences": {
                "recent_memories": recent_memories,
                "animal_interactions": agent.animal_interactions,
                "domesticated_animals": agent.domesticated_animals
            },
            "cognition_state": cognition.get_state() if cognition else None
        }
        
        return agent_json

    def get_animal_json(self, animal_id: str) -> Dict:
        """Generate a comprehensive JSON representation of an animal's complete state."""
        if animal_id not in self.animals.animals:
            return {}
            
        animal = self.animals.animals[animal_id]
        
        # Get animal's current location and environment
        terrain = self.environment.get_terrain_at(*animal.position)
        climate = self.environment.get_climate_at(*animal.position)
        weather = self.environment.get_weather_at(*animal.position)
        
        # Build comprehensive JSON
        animal_json = {
            "basic_info": {
                "id": animal.id,
                "species": animal.species,
                "age": animal.age,
                "life_stage": animal.life_stage.value,
                "is_dead": animal.is_dead,
                "position": animal.position,
                "genes": animal.genes.__dict__
            },
            "physical_state": {
                "health": animal.health.to_dict(),
                "needs": animal.needs.__dict__,
                "diseases": animal.diseases,
                "injuries": animal.injuries,
                "strength": animal.genes.strength,
                "adaptability": animal.genes.adaptability
            },
            "behavior": {
                "temperament": animal.temperament,
                "social_behavior": animal.social_behavior,
                "territorial_behavior": animal.territorial_behavior,
                "migration_pattern": animal.migration_pattern,
                "hunting_behavior": animal.hunting_behavior,
                "reproduction_behavior": animal.reproduction_behavior
            },
            "social_state": {
                "pack": animal.pack,
                "hierarchy": animal.hierarchy,
                "relationships": animal.relationships,
                "enemies": list(animal.enemies),
                "allies": list(animal.allies)
            },
            "family": {
                "parents": animal.parents,
                "offspring": animal.offspring,
                "mate": animal.mate
            },
            "environment": {
                "terrain": terrain.type.value if terrain else "unknown",
                "climate": climate.get("terrain_type", "unknown"),
                "weather": weather.get("type", "unknown").value,
                "resources": self.resources.get_resources_at(animal.position)
            },
            "interactions": {
                "human_interactions": animal.human_interactions,
                "predator_interactions": animal.predator_interactions,
                "prey_interactions": animal.prey_interactions,
                "territory_markers": animal.territory_markers
            },
            "domestication": {
                "is_domesticated": animal.is_domesticated,
                "domestication_level": animal.domestication_level,
                "owner": animal.owner,
                "training": animal.training,
                "usefulness": animal.usefulness
            }
        }
        
        return animal_json

    def get_state(self) -> Dict:
        """Get current simulation state."""
        return {
            "tick": self.current_tick,
            "simulation_time": self.simulation_time,
            "running": self.running,
            "world": self.to_dict()
        }

    def get_state_for_agent(self, agent: Agent) -> Dict:
        """Get world state relevant to a specific agent."""
        return {
            "environment": self.environment,
            "resources": self.resources,
            "agents": {aid: a.to_dict() for aid, a in self.agents.items() if aid != agent.id},
            "animals": {animal.id: animal.to_dict() for animal in self.animals.animals.values()},
            "time": self.game_time,
            "world_size": (self.environment.width, self.environment.height),
            "explored_area": self._get_explored_area(agent.position),
            "nearby_resources": self.environment.get_nearby_resources(*agent.position, radius=5),
            "nearby_climate": self.environment.get_nearby_climate(*agent.position, radius=5),
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
            for test_lon in range(int(min_lon / self.longitude_resolution),
                                int(max_lon / self.longitude_resolution) + 1):
                for test_lat in range(int(min_lat / self.latitude_resolution),
                                    int(max_lat / self.latitude_resolution) + 1):
                    test_lon = test_lon * self.longitude_resolution
                    test_lat = test_lat * self.latitude_resolution
                    
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
                        if agent_id in self.agents:
                            # Update agent with saved data
                            self.agents[agent_id].update_from_save(data)
                except Exception as e:
                    logger.error(f"Error loading agent data for {agent_id}: {str(e)}")
                    
    def save_agent_data(self, agent_id: str = None):
        """Save agent data to JSON files."""
        if agent_id:
            # Save single agent
            agents_to_save = {agent_id: self.agents[agent_id]}
        else:
            # Save all agents
            agents_to_save = self.agents
            
        for aid, agent in agents_to_save.items():
            try:
                data = agent.to_dict()
                data['last_saved'] = datetime.now().isoformat()
                
                with open(os.path.join(self.db_dir, f"{aid}.json"), 'w') as f:
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
