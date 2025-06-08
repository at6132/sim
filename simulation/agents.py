from typing import Dict, List, Optional, Set, Tuple
import uuid
import time
from datetime import datetime
from .utils.logging_config import get_logger
import math
from .cooking import CookingSystem, FoodType
import random

class Agent:
    def __init__(self, agent_id: str, name: str, position: Tuple[float, float]):
        self.id = agent_id
        self.name = name
        self.position = position
        self.health = 100.0
        self.energy = 100.0
        self.hunger = 0.0
        self.thirst = 0.0
        self.age = 0
        self.skills = {}
        self.inventory = {}
        self.created_at = time.time()
        self.last_update = time.time()
        self.last_action = None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'health': self.health,
            'energy': self.energy,
            'hunger': self.hunger,
            'thirst': self.thirst,
            'age': self.age,
            'skills': self.skills,
            'inventory': self.inventory,
            'created_at': self.created_at,
            'last_update': self.last_update,
            'last_action': self.last_action
        }

class AgentSystem:
    def __init__(self, world):
        self.world = world
        self.logger = get_logger(__name__)
        
        # Initialize agent storage
        self.agents = {}  # agent_id -> Agent
        self.agent_positions = {}  # (lon, lat) -> Set[agent_id]
        self.agent_groups = {}  # agent_id -> group_id
        
        self.logger.info("Agent system initialized")
    
    def initialize_agents(self):
        """Initialize the agent system with basic structures."""
        self.logger.info("Initializing agent system...")
        
        # Create initial agents
        self._create_initial_agents()
        
        self.logger.info("Agent system initialization complete")
    
    def _create_initial_agents(self):
        """Create the initial set of agents."""
        self.logger.info("Creating initial agents...")
        
        # Passaic, New Jersey coordinates
        passaic_lon = -74.1285  # Longitude
        passaic_lat = 40.8576   # Latitude
        
        # Create two agents near Passaic
        initial_positions = [
            (passaic_lon, passaic_lat),  # First agent at Passaic
            (passaic_lon + 0.01, passaic_lat + 0.01)  # Second agent slightly offset
        ]
        
        for i, position in enumerate(initial_positions):
            agent_id = str(uuid.uuid4())
            name = f"Agent_{i+1}"
            
            agent = Agent(
                agent_id=agent_id,
                name=name,
                position=position
            )
            
            # Initialize basic skills
            agent.skills = {
                'hunting': 0.3,
                'gathering': 0.3,
                'crafting': 0.2
            }
            
            # Initialize basic inventory
            agent.inventory = {
                'food': 10.0,
                'water': 10.0,
                'tools': 1
            }
            
            # Add agent to storage
            self.agents[agent_id] = agent
            self.agent_positions[position] = {agent_id}
            
            self.logger.info(f"Created agent {name} at position {position}")

    def create_agent(self, longitude: float, latitude: float, name: Optional[str] = None,
                     parent_id: Optional[str] = None) -> str:
        """Create a new agent and add it to the system."""
        agent_id = str(uuid.uuid4())
        if name is None:
            name = f"Agent_{len(self.agents) + 1}"

        agent = Agent(agent_id=agent_id, name=name, position=(longitude, latitude))

        self.agents[agent_id] = agent
        if (longitude, latitude) not in self.agent_positions:
            self.agent_positions[(longitude, latitude)] = set()
        self.agent_positions[(longitude, latitude)].add(agent_id)

        if parent_id is not None:
            self.agent_groups[agent_id] = self.agent_groups.get(parent_id)

        self.logger.info(f"Created agent {agent_id} at ({longitude}, {latitude})")
        return agent_id

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Retrieve an agent by ID."""
        return self.agents.get(agent_id)
    
    def update(self, time_delta: float):
        """Update agent states."""
        self.logger.debug(f"Updating agents with time delta: {time_delta}")
        
        for agent_id, agent in self.agents.items():
            # Update basic needs
            self._update_agent_needs(agent, time_delta)
            
            # Update agent position
            self._update_agent_position(agent, time_delta)
            
            # Update agent skills
            self._update_agent_skills(agent, time_delta)
            
            # Update agent inventory
            self._update_agent_inventory(agent, time_delta)
    
    def _update_agent_needs(self, agent: Agent, time_delta: float):
        """Update agent's basic needs."""
        # Increase hunger and thirst over time
        agent.hunger = min(100.0, agent.hunger + 0.1 * time_delta)
        agent.thirst = min(100.0, agent.thirst + 0.15 * time_delta)
        
        # Decrease energy based on hunger and thirst
        energy_loss = (agent.hunger + agent.thirst) * 0.01 * time_delta
        agent.energy = max(0.0, agent.energy - energy_loss)
        
        # Decrease health if energy is too low
        if agent.energy < 20.0:
            agent.health = max(0.0, agent.health - 0.1 * time_delta)
    
    def _update_agent_position(self, agent: Agent, time_delta: float):
        """Update agent's position considering terrain and energy costs."""
        # Get current terrain info
        current_terrain = self.world.terrain.get_terrain_info_at(*agent.position)
        current_elevation = self.world.terrain.get_elevation_at(*agent.position)
        current_slope = self.world.terrain.get_slope_at(*agent.position)
        
        # Calculate movement cost based on terrain
        movement_cost = self._calculate_movement_cost(current_terrain, current_slope)
        
        # Check if agent has enough energy to move
        if agent.energy < movement_cost:
            # Agent is too tired to move
            agent.last_action = "resting"
            agent.energy = min(100.0, agent.energy + 0.5 * time_delta)  # Rest and recover energy
            return
        
        # Calculate possible movement range based on energy
        max_distance = min(0.01 * time_delta, agent.energy / movement_cost)
        
        # Generate random movement within energy constraints
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, max_distance)
        
        # Calculate new position
        lon, lat = agent.position
        new_lon = lon + distance * math.cos(angle)
        new_lat = lat + distance * math.sin(angle)
        
        # Check if new position is valid
        if not self._is_valid_position(new_lon, new_lat):
            return
        
        # Get terrain at new position
        new_terrain = self.world.terrain.get_terrain_info_at(new_lon, new_lat)
        new_elevation = self.world.terrain.get_elevation_at(new_lon, new_lat)
        new_slope = self.world.terrain.get_slope_at(new_lon, new_lat)
        
        # Calculate elevation change cost
        elevation_change = abs(new_elevation - current_elevation)
        elevation_cost = elevation_change * 2.0  # Climbing/descending costs more energy
        
        # Check if agent has enough energy for the elevation change
        if agent.energy < (movement_cost + elevation_cost):
            return
        
        # Update position
        old_position = agent.position
        agent.position = (new_lon, new_lat)
        
        # Update energy based on movement and terrain
        agent.energy = max(0.0, agent.energy - (movement_cost + elevation_cost))
        
        # Update position tracking
        if old_position in self.agent_positions:
            self.agent_positions[old_position].remove(agent.id)
            if not self.agent_positions[old_position]:
                del self.agent_positions[old_position]
        
        if agent.position not in self.agent_positions:
            self.agent_positions[agent.position] = set()
        self.agent_positions[agent.position].add(agent.id)
        
        # Update last action
        if elevation_change > 0:
            agent.last_action = "climbing" if new_elevation > current_elevation else "descending"
        else:
            agent.last_action = "moving"
    
    def _calculate_movement_cost(self, terrain_info: Dict, slope: float) -> float:
        """Calculate the energy cost of movement based on terrain and slope."""
        base_cost = 1.0
        
        # Terrain-specific costs
        terrain_costs = {
            "MOUNTAIN": 5.0,
            "HILLS": 3.0,
            "FOREST": 2.0,
            "SWAMP": 4.0,
            "RIVER": 3.0,
            "LAKE": 5.0,  # Can't move through lakes
            "OCEAN": 10.0,  # Can't move through oceans
            "GLACIER": 6.0,
            "DESERT": 2.0,
            "GRASSLAND": 1.0,
            "PLAINS": 1.0
        }
        
        terrain_type = terrain_info.get("type", "PLAINS")
        terrain_cost = terrain_costs.get(terrain_type, 1.0)
        
        # Slope cost (0-1 scale)
        slope_cost = 1.0 + (slope * 4.0)  # Steeper slopes cost more energy
        
        return base_cost * terrain_cost * slope_cost
    
    def _is_valid_position(self, lon: float, lat: float) -> bool:
        """Check if a position is valid for movement."""
        # Check world bounds
        if not (self.world.min_longitude <= lon <= self.world.max_longitude and
                self.world.min_latitude <= lat <= self.world.max_latitude):
            return False
        
        # Check if position is in impassable terrain
        terrain_info = self.world.terrain.get_terrain_info_at(lon, lat)
        terrain_type = terrain_info.get("type", "PLAINS")
        
        impassable_terrain = {
            "OCEAN",
            "LAKE",
            "RIVER",  # Rivers are passable but with high cost
            "GLACIER"  # Glaciers are passable but with high cost
        }
        
        return terrain_type not in impassable_terrain
    
    def _update_agent_skills(self, agent: Agent, time_delta: float):
        """Update agent's skills."""
        # Skills improve slightly over time
        for skill in agent.skills:
            improvement = 0.001 * time_delta
            agent.skills[skill] = min(1.0, agent.skills[skill] + improvement)
    
    def _update_agent_inventory(self, agent: Agent, time_delta: float):
        """Update agent's inventory and handle food consumption using CookingSystem."""
        cooking_system = CookingSystem()
        food_items = [item for item in agent.inventory if item in FoodType._value2member_map_]
        ate_food = False
        for food_item in food_items:
            if agent.hunger > 50.0 and agent.inventory[food_item] > 0:
                food_type = FoodType(food_item)
                props = cooking_system.get_food_properties(food_type)
                if not props:
                    continue
                # Consume one unit of food
                agent.inventory[food_item] = max(0.0, agent.inventory[food_item] - 1.0)
                # Update hunger
                agent.hunger = max(0.0, agent.hunger - props.nutritional_value)
                # Health effect
                agent.health = max(0.0, min(100.0, agent.health + props.health_effect))
                # Sickness risk
                if props.food_safety_risk > 50.0 and random.random() < (props.food_safety_risk / 100.0):
                    agent.health = max(0.0, agent.health - 20.0)  # Sickness penalty
                ate_food = True
                break  # Only eat one food per update
        # Water logic (unchanged)
        if agent.thirst > 50.0 and 'water' in agent.inventory:
            agent.inventory['water'] = max(0.0, agent.inventory['water'] - 0.15 * time_delta)
            agent.thirst = max(0.0, agent.thirst - 0.3 * time_delta)
    
    def get_state(self) -> Dict:
        """Get the current state of the agent system."""
        return {
            'agents': {
                agent_id: {
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
                    'created_at': agent.created_at,
                    'last_update': agent.last_update,
                    'last_action': agent.last_action
                }
                for agent_id, agent in self.agents.items()
            },
            'agent_positions': {
                f"{pos[0]},{pos[1]}": list(agent_ids)
                for pos, agent_ids in self.agent_positions.items()
            }
        } 