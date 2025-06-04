from typing import Dict, List, Optional, Tuple, Set
import random
import uuid
import logging
from datetime import datetime, timedelta
from .agent import Agent, Genes
from .environment import Environment
from .terrain import TerrainType
from .llm import AgentCognition
from .biology import BiologicalSystem
from .technology import TechnologyTree
from .resources import ResourceSystem, ResourceType
from .society import Society, SocialStructure, Culture, Settlement
from .discovery import DiscoverySystem, Discovery
from simulation.animal import AnimalSystem
from .life_cycle import LifeCycleSystem
from .philosophy import Philosophy
from .emotions import EmotionSystem
from .health import Health
from .relationships import Relationships
from .economy import EconomicSystem
from simulation.transportation import TransportationSystem, TransportationType
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
import numpy as np
import pickle
import traceback
import concurrent.futures
from .utils.logging_config import get_logger
from .agents import AgentSystem
from .transportation import TransportationSystem

logger = get_logger(__name__)

class World:
    @classmethod
    def load_from_save(cls):
        """Try to load the most recent world state."""
        save_dir = "simulation_saves"
        if not os.path.exists(save_dir):
            return None
            
        # Get all save directories
        save_dirs = [d for d in os.listdir(save_dir) if d.startswith("world_state_")]
        if not save_dirs:
            return None
            
        # Get most recent save
        latest_save = max(save_dirs, key=lambda x: os.path.getctime(os.path.join(save_dir, x)))
        save_path = os.path.join(save_dir, latest_save)
        
        try:
            # Load world state
            with open(os.path.join(save_path, "world.pkl"), 'rb') as f:
                world = pickle.load(f)
            logger.info(f"Loaded world state from {save_path}")
            return world
        except Exception as e:
            logger.error(f"Error loading world state: {e}")
            return None

    def __init__(self):
        """Initialize the world."""
        logger.info("Initializing world...")
        
        # Define coordinate ranges
        self.longitude_range = range(-180, 181, 1)  # 1-degree resolution
        self.latitude_range = range(-90, 91, 1)     # 1-degree resolution
        
        # Initialize systems
        self.terrain = TerrainSystem(self)
        self.climate = ClimateSystem(self)
        self.resources = ResourceSystem(self)
        self.agents = AgentSystem(self)
        self.society = SocietySystem(self)
        self.transportation = TransportationSystem(self)
        
        # Initialize world state
        self.time = 0.0  # Current time in minutes
        self.day_length = 24 * 60  # 24 hours in minutes
        self.year_length = 365 * self.day_length  # 365 days in minutes
        
        logger.info("World initialization complete")
        
    def update(self, time_delta: float):
        """Update the world state."""
        logger.info(f"Updating world state for {time_delta} minutes...")
        
        # Update time
        self.time += time_delta
        
        # Update all systems
        self.terrain.update(time_delta)
        self.climate.update(time_delta)
        self.resources.update(time_delta)
        self.agents.update(time_delta)
        self.society.update(time_delta)
        self.transportation.update(time_delta)
        
        logger.info("World state update complete")
        
    def get_state(self) -> Dict:
        """Get the current world state."""
        return {
            'time': self.time,
            'terrain': self.terrain.get_state(),
            'climate': self.climate.get_state(),
            'resources': self.resources.get_state(),
            'agents': self.agents.get_state(),
            'society': self.society.get_state(),
            'transportation': self.transportation.get_state()
        }
        
    def to_dict(self):
        """Convert world state to dictionary."""
        return self.get_state()
        
    def spawn_initial_agents(self, count: int = 1):
        """Spawn initial agents."""
        for _ in range(count):
            # Find suitable spawn location
            lon = random.uniform(self.min_longitude, self.max_longitude)
            lat = random.uniform(self.min_latitude, self.max_latitude)
            
            # Create and add agent
            agent = Agent(lon, lat)
            self.agents.append(agent)
            
    def _initialize_world(self):
        """Initialize the world and all its systems."""
        if self._init_count > 0:
            logger.warning("World already initialized, skipping initialization")
            return
            
        logger.info("Initializing world...")
        self._init_count += 1
        
        # Initialize terrain first (required by other systems)
        self.terrain.initialize_terrain()
        
        # Initialize climate (required for spawning)
        self.climate.initialize_earth_climate()
        
        # Initialize resources
        self.resources.initialize_resources()
        
        # Initialize plants with initial populations
        self.plants.initialize_plants()
        
        # Initialize animals with initial populations
        self.animal_system.initialize_animals()
        
        # Initialize marine life with initial populations
        self.marine_system.initialize_marine()
        
        # Initialize technology
        self.technology.initialize_technology()
        
        # Initialize society and transportation after all other systems
        self.society.initialize_society()
        self.transportation.initialize_transportation()
        
        # Create initial agents (Avi and Yehudit)
        self._create_initial_agents()
        
        # Verify all systems are properly initialized
        if not self.verify_initialization():
            logger.error("World initialization verification failed")
            raise RuntimeError("World initialization verification failed")
        
        logger.info("World initialization complete")
        
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
        if not hasattr(self.animal_system, 'creatures') or not self.animal_system.creatures:
            logger.error("Animal system not properly initialized")
            return False
            
        # Verify marine system
        if not hasattr(self.marine_system, 'creatures') or not self.marine_system.creatures:
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

    def _create_initial_agents(self) -> None:
        """Create initial agents without names."""
        logger.info("Creating initial agents without names")
        
        # Create first agent
        agent1 = Agent(
            id="agent_1",
            name="",  # Empty name, will be developed through interactions
            age=20,
            gender="unknown",
            genes=Genes(),  # Use default Genes initialization
            needs=AgentNeeds(),
            memory=Memory(),
            emotions=EmotionSystem(),
            health=1.0,
            philosophy=Philosophy(),
            longitude=0.0,
            latitude=0.0
        )
        
        # Create second agent
        agent2 = Agent(
            id="agent_2",
            name="",  # Empty name, will be developed through interactions
            age=20,
            gender="unknown",
            genes=Genes(),  # Use default Genes initialization
            needs=AgentNeeds(),
            memory=Memory(),
            emotions=EmotionSystem(),
            health=1.0,
            philosophy=Philosophy(),
            longitude=1.0,
            latitude=1.0
        )
        
        # Add agents to world
        self.agents.append(agent1)
        self.agents.append(agent2)
        
        logger.info(f"Created initial agents with IDs: {agent1.id}, {agent2.id}")

    def spawn_initial_agents(self, num_agents: int = 2) -> None:
        """Spawn initial agents without names."""
        logger.info(f"Spawning {num_agents} initial agents without names")
        
        for i in range(num_agents):
            # Generate random position
            longitude = random.uniform(-180, 180)
            latitude = random.uniform(-90, 90)
            
            # Create agent
            agent = Agent(
                id=f"agent_{i}",
                name="",  # Empty name, will be developed through interactions
                age=20,
                gender="unknown",
                genes=Genes(),
                needs=AgentNeeds(),
                memory=Memory(),
                emotions=EmotionSystem(),
                health=1.0,
                philosophy=Philosophy(),
                longitude=longitude,
                latitude=latitude
            )
            
            # Add agent to world
            self.agents.append(agent)
            
        logger.info(f"Spawned {num_agents} agents with IDs: {', '.join(agent.id for agent in self.agents)}")

    def get_world_state(self) -> Dict:
        """Get current world state for agents."""
        return {
            "time": self.game_time,
            "terrain": self.terrain.get_state(),
            "climate": self.climate.get_state(),
            "weather": self.weather.get_state(),
            "resources": self.resources.get_state(),
            "transportation": self.transportation.get_state(),
            "settlements": {id: settlement.get_state() for id, settlement in self.settlements.items()},
            "agents": {id: agent.get_state() for id, agent in self.agents.items()},
            "marine": self.marine_system.get_state(),
            "environmental_conditions": {
                "temperature": self.climate.get_temperature_at,
                "salinity": self.terrain.get_salinity_at,
                "oxygen": self.terrain.get_oxygen_at,
                "current": self.terrain.get_current_at,
                "depth": self.terrain.get_depth_at,
                "tidal_range": self.terrain.get_tidal_range_at
            }
        }
        
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
        
        self.agents.append(agent)
        
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
            self.agents.remove(agent_id)
            
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
        if animal_id not in self.animal_system.animals:
            return {}
            
        animal = self.animal_system.animals[animal_id]
        
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
            "animals": {animal.id: animal.to_dict() for animal in self.animal_system.animals.values()},
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
            "marine": self.marine_system.get_state()
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
        if creature_id not in self.marine_system.creatures:
            return None
        
        creature = self.marine_system.creatures[creature_id]
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
            'marine': self.marine_system,
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
        self.marine_system = state['marine']
        self.min_longitude = state['min_longitude']
        self.max_longitude = state['max_longitude']
        self.min_latitude = state['min_latitude']
        self.max_latitude = state['max_latitude']
        self.longitude_resolution = state['longitude_resolution']
        self.latitude_resolution = state['latitude_resolution']
        
        # Restore world references
        self.terrain.world = self
        self.climate.world = self
        self.marine_system.world = self

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
                        "center": (lon, lat),
                        "terrain_type": terrain.value if hasattr(terrain, 'value') else terrain,  # Handle both enum and string
                        "size": 5000  # Approximate size in square kilometers
                    })
        
        return regions

    def _save_state(self):
        """Save the current world state to disk."""
        try:
            logger.info("[SAVE] Attempting to save world state...")
            saves_dir = 'simulation_saves'
            os.makedirs(saves_dir, exist_ok=True)
            
            # Create timestamped save directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_dir = os.path.join(saves_dir, f'world_state_{timestamp}')
            os.makedirs(save_dir)
            
            # Save each system's state with complete data
            systems = {
                'terrain': self.terrain,
                'climate': self.climate,
                'resources': self.resources,
                'plants': self.plants,
                'animals': self.animal_system,
                'marine': self.marine_system,
                'technology': self.technology,
                'society': self.society,
                'transportation': self.transportation
            }
            
            for name, system in systems.items():
                try:
                    # Get complete system state
                    if hasattr(system, 'get_state'):
                        state = system.get_state()
                    elif hasattr(system, 'to_dict'):
                        state = system.to_dict()
                    else:
                        # For systems without state methods, save all attributes
                        state = {
                            'type': system.__class__.__name__,
                            'initialized': True,
                            'attributes': {k: v for k, v in system.__dict__.items() 
                                         if not k.startswith('_') and k != 'world'}
                        }
                    
                    # Ensure we have complete data for each system
                    if name == 'terrain':
                        state.update({
                            'height_map': system.height_map.tolist() if hasattr(system, 'height_map') else [],
                            'biome_map': system.biome_map.tolist() if hasattr(system, 'biome_map') else [],
                            'water_map': system.water_map.tolist() if hasattr(system, 'water_map') else [],
                            'resource_map': system.resource_map.tolist() if hasattr(system, 'resource_map') else []
                        })
                    elif name == 'marine':
                        state.update({
                            'creatures': {cid: creature.to_dict() for cid, creature in system.creatures.items()},
                            'social_groups': {gid: group.to_dict() for gid, group in system.social_groups.items()},
                            'territories': {tid: territory.to_dict() for tid, territory in system.territories.items()},
                            'spatial_grid': system.spatial_grid if hasattr(system, 'spatial_grid') else {}
                        })
                    elif name == 'animals':
                        state.update({
                            'creatures': {cid: creature.to_dict() for cid, creature in system.creatures.items()},
                            'social_groups': {gid: group.to_dict() for gid, group in system.social_groups.items()},
                            'territories': {tid: territory.to_dict() for tid, territory in system.territories.items()},
                            'mating_pairs': system.mating_pairs if hasattr(system, 'mating_pairs') else {}
                        })
                    elif name == 'plants':
                        state.update({
                            'plants': {pid: plant.to_dict() for pid, plant in system.plants.items()},
                            'growth_stages': system.growth_stages if hasattr(system, 'growth_stages') else {},
                            'biome_distribution': system.biome_distribution if hasattr(system, 'biome_distribution') else {}
                        })
                    elif name == 'climate':
                        state.update({
                            'temperature_map': system.temperature_map.tolist() if hasattr(system, 'temperature_map') else [],
                            'precipitation_map': system.precipitation_map.tolist() if hasattr(system, 'precipitation_map') else [],
                            'wind_map': system.wind_map.tolist() if hasattr(system, 'wind_map') else [],
                            'current_conditions': system.current_conditions if hasattr(system, 'current_conditions') else {}
                        })
                    elif name == 'society':
                        state.update({
                            'tribes': {tid: tribe.to_dict() for tid, tribe in system.tribes.items()},
                            'relationships': system.relationships if hasattr(system, 'relationships') else {},
                            'social_structures': system.social_structures if hasattr(system, 'social_structures') else {},
                            'cultural_traits': system.cultural_traits if hasattr(system, 'cultural_traits') else {}
                        })
                    elif name == 'technology':
                        state.update({
                            'technologies': {tid: tech.to_dict() for tid, tech in system.technologies.items()},
                            'innovations': {iid: innovation.to_dict() for iid, innovation in system.innovations.items()},
                            'discoveries': system.discoveries if hasattr(system, 'discoveries') else [],
                            'research_progress': system.research_progress if hasattr(system, 'research_progress') else {}
                        })
                        
                    save_path = os.path.join(save_dir, f'{name}.json')
                    with open(save_path, 'w') as f:
                        json.dump(state, f, indent=2)
                    logger.info(f"[SAVE] Saved {name} state to {save_path}")
                except Exception as sys_e:
                    logger.error(f"[SAVE] Error saving {name}: {sys_e}")
                    logger.error(traceback.format_exc())
            
            # Save world state with complete data
            world_state = {
                'time': self.time,
                'current_tick': self.current_tick,
                'simulation_time': self.simulation_time,
                'game_time': self.game_time.isoformat(),
                'real_time_start': self.real_time_start.isoformat(),
                'game_time_start': self.game_time_start.isoformat(),
                'time_scale': self.time_scale,
                'current_season': self.current_season,
                'current_weather': self.current_weather,
                'temperature': self.temperature,
                'humidity': self.humidity,
                'wind_speed': self.wind_speed,
                'wind_direction': self.wind_direction,
                'precipitation': self.precipitation,
                'cloud_cover': self.cloud_cover,
                'air_pressure': self.air_pressure,
                'visibility': self.visibility,
                'agents': {aid: agent.to_dict() for aid, agent in self.agents.items()},
                'settlements': {sid: settlement.to_dict() for sid, settlement in self.settlements.items()},
                'events': self.events[-1000:],  # Keep last 1000 events
                'spatial_grid': self.spatial_grid if hasattr(self, 'spatial_grid') else {},
                'resource_distribution': self.resource_distribution if hasattr(self, 'resource_distribution') else {},
                'biome_distribution': self.biome_distribution if hasattr(self, 'biome_distribution') else {}
            }
            
            # Save world state
            world_state_path = os.path.join(save_dir, 'world_state.json')
            with open(world_state_path, 'w') as f:
                json.dump(world_state, f, indent=2)
            logger.info(f"[SAVE] Saved world state to {world_state_path}")
            
            # Save metadata with complete system info
            metadata = {
                'timestamp': timestamp,
                'systems': list(systems.keys()),
                'world_version': '1.0',
                'save_time': datetime.now().isoformat(),
                'initialization_count': getattr(self, '_init_count', 0),
                'system_versions': {
                    name: getattr(system, 'version', '1.0') for name, system in systems.items()
                },
                'data_completeness': {
                    name: {
                        'has_state_method': hasattr(system, 'get_state'),
                        'has_dict_method': hasattr(system, 'to_dict'),
                        'attributes_saved': len(getattr(system, '__dict__', {}))
                    } for name, system in systems.items()
                }
            }
            metadata_path = os.path.join(save_dir, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"[SAVE] Successfully saved world state to {save_dir}")
            return True
            
        except Exception as e:
            logger.error(f"[SAVE] Critical error saving world state: {str(e)}")
            logger.error(traceback.format_exc())
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
                
            metadata_path = os.path.join(save_dir, 'metadata.json')
            if not os.path.exists(metadata_path):
                logger.info(f"[LOAD] Metadata file not found in {save_dir}")
                return False
                
            logger.info(f"[LOAD] Loading from directory: {save_dir}")
            
            # Load metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            logger.info(f"[LOAD] Loaded metadata: {metadata}")
            
            # Load each system's state
            systems = {
                'terrain': self.terrain,
                'climate': self.climate,
                'resources': self.resources,
                'plants': self.plants,
                'animals': self.animal_system,
                'marine': self.marine_system,
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
