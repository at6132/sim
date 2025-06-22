from typing import Dict, List, Optional, Set, Tuple, Any
import uuid
import time
from datetime import datetime
from .utils.logging_config import get_logger
import math
from .cooking import CookingSystem, FoodType
import random
from dataclasses import dataclass

@dataclass
class Agent:
    """Represents an agent in the simulation."""
    id: str
    position: Tuple[float, float]
    health: float
    energy: float
    hunger: float
    thirst: float
    age: int
    skills: Dict[str, float]
    inventory: Dict[str, Any]
    last_action: Optional[str]
    name: Optional[str] = None
    world: Optional[Any] = None  # Reference to world for movement validation
    logger: Optional[Any] = None  # Logger for agent-specific logging
    gender: str = 'unknown'
    velocity: Tuple[float, float] = (0.0, 0.0)
    mass: float = 70.0

    def get_state(self) -> Dict:
        """Get current agent state for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "health": self.health,
            "energy": self.energy,
            "hunger": self.hunger,
            "thirst": self.thirst,
            "age": self.age,
            "skills": self.skills,
            "inventory": self.inventory,
            "last_action": self.last_action,
            "velocity": self.velocity,
            "mass": self.mass
        }

    def _is_valid_position(self, longitude: float, latitude: float) -> bool:
        """Check if a position is valid for movement."""
        # Check world bounds
        if not (self.world.min_longitude <= longitude <= self.world.max_longitude and
                self.world.min_latitude <= latitude <= self.world.max_latitude):
            return False
            
        # All positions are valid, including water
        return True

    def move(self, target_longitude: float, target_latitude: float) -> bool:
        """Move agent to target position."""
        # Calculate distance to target
        distance = self.world.get_distance(
            self.position[0], self.position[1],
            target_longitude, target_latitude
        )
        
        # Get terrain type at target
        terrain_info = self.world.terrain.get_terrain_info_at(target_longitude, target_latitude)
        terrain_type = terrain_info.get('type', 'UNKNOWN')
        
        # Calculate movement cost based on terrain and slope
        base_cost = distance * 10  # Base cost per unit distance
        terrain_cost = {
            "PLAINS": 1.0,
            "FOREST": 1.5,
            "MOUNTAINS": 2.0,
            "DESERT": 1.2,
            "OCEAN": 2.5,  # Swimming is more energy intensive
            "LAKE": 2.0,
            "RIVER": 1.8
        }.get(terrain_type, 1.0)
        
        slope = self.world.terrain.get_slope_at(target_longitude, target_latitude)
        slope_cost = 1.0 + abs(slope) * 0.5
        
        total_cost = base_cost * terrain_cost * slope_cost
        
        # Check if agent has enough energy
        if self.energy < total_cost:
            self.logger.info(f"Agent {self.name} doesn't have enough energy to move (needs {total_cost}, has {self.energy})")
            return False
            
        # Handle water movement
        if terrain_type in ["OCEAN", "LAKE", "RIVER"]:
            # Check if agent can swim (based on skills or equipment)
            can_swim = self.skills.get("swimming", 0) > 0.3 or "swimming_gear" in self.inventory
            
            if not can_swim:
                # Risk of drowning
                if random.random() < 0.3:  # 30% chance of drowning
                    self.health -= 20
                    self.logger.info(f"Agent {self.name} is drowning in {terrain_type}!")
                    if self.health <= 0:
                        self.logger.info(f"Agent {self.name} has drowned!")
                        return False
                else:
                    # Struggle to stay afloat
                    self.energy -= total_cost * 1.5
                    self.logger.info(f"Agent {self.name} is struggling in {terrain_type}")
            else:
                # Swimming is more energy intensive
                self.energy -= total_cost * 1.2
                self.logger.info(f"Agent {self.name} is swimming in {terrain_type}")
        else:
            # Normal movement
            self.energy -= total_cost
            
        # Update position
        self.position = (target_longitude, target_latitude)
        self.last_action = "move"
        self.logger.info(f"Agent {self.name} moved to ({target_longitude}, {target_latitude})")
        return True


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
        # Just initialize the system, don't create agents yet
        self.logger.info("Agent system initialization complete")
    
    def _create_initial_agents(self):
        """Create initial agents in the world."""
        # Passaic, New Jersey coordinates (adjusted to be on land)
        base_longitude = -74.1295  # Passaic longitude
        base_latitude = 40.8574    # Passaic latitude
        
        # Create first agent
        agent1 = Agent(
            id=str(uuid.uuid4()),
            name=None,
            position=(base_longitude + 0.01, base_latitude + 0.01),  # Slightly offset to ensure on land
            health=100.0,
            energy=100.0,
            hunger=0.0,
            thirst=0.0,
            age=20,
            skills={
                "hunting": 0.3,
                "gathering": 0.3,
                "crafting": 0.2,
                "swimming": 0.1
            },
            inventory={},
            last_action=None,
            world=self.world  # Pass world reference
        )
        self.agents[agent1.id] = agent1
        self.logger.info(f"Created agent {agent1.name} at position {agent1.position}")
        
        # Create second agent
        agent2 = Agent(
            id=str(uuid.uuid4()),
            name=None,
            position=(base_longitude - 0.01, base_latitude - 0.01),  # Slightly offset in opposite direction
            health=100.0,
            energy=100.0,
            hunger=0.0,
            thirst=0.0,
            age=20,
            skills={
                "hunting": 0.3,
                "gathering": 0.3,
                "crafting": 0.2,
                "swimming": 0.1
            },
            inventory={},
            last_action=None,
            world=self.world  # Pass world reference
        )
        self.agents[agent2.id] = agent2
        self.logger.info(f"Created agent {agent2.name} at position {agent2.position}")

    def create_agent(self, longitude: float, latitude: float, name: Optional[str] = None,
                     parent_id: Optional[str] = None, gender: str = 'unknown') -> str:
        """Create a new agent and add it to the system."""
        agent_id = str(uuid.uuid4())

        agent = Agent(
            id=agent_id,
            name=name,
            position=(longitude, latitude),
            health=100.0,
            energy=100.0,
            hunger=0.0,
            thirst=0.0,
            age=20,
            skills={
                "hunting": 0.3,
                "gathering": 0.3,
                "crafting": 0.2,
                "swimming": 0.1
            },
            inventory={},
            last_action=None,
            world=self.world,  # Pass world reference
            logger=self.logger,  # Pass logger reference
            gender=gender,
            velocity=(0.0, 0.0),
            mass=70.0
        )

        self.agents[agent_id] = agent
        if (longitude, latitude) not in self.agent_positions:
            self.agent_positions[(longitude, latitude)] = set()
        self.agent_positions[(longitude, latitude)].add(agent_id)

        # Register the new agent with the physics system if available
        if hasattr(self.world, "physics") and self.world.physics:
            self.world.physics.register_agent(agent)

        if parent_id is not None:
            self.agent_groups[agent_id] = self.agent_groups.get(parent_id)

        self.logger.info(f"Created agent {agent_id} at ({longitude}, {latitude})")
        return agent_id

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Retrieve an agent by ID."""
        return self.agents.get(agent_id)
    
    def update(self, time_delta: float):
        """Update agent states."""
        self.logger.info(f"Updating {len(self.agents)} agents with time delta: {time_delta}")
        
        for agent_id, agent in self.agents.items():
            # Log initial state
            self.logger.info(f"Agent {agent.name} ({agent_id}) - Initial state: "
                           f"Health: {agent.health:.1f}, Energy: {agent.energy:.1f}, "
                           f"Hunger: {agent.hunger:.1f}, Thirst: {agent.thirst:.1f}")
            
            # Update basic needs
            self._update_agent_needs(agent, time_delta)
            
            # Update agent position
            self._update_agent_position(agent, time_delta)
            
            # Update agent skills
            self._update_agent_skills(agent, time_delta)
            
            # Update agent inventory
            self._update_agent_inventory(agent, time_delta)
            
            # Log final state
            self.logger.info(f"Agent {agent.name} ({agent_id}) - Final state: "
                           f"Health: {agent.health:.1f}, Energy: {agent.energy:.1f}, "
                           f"Hunger: {agent.hunger:.1f}, Thirst: {agent.thirst:.1f}, "
                           f"Action: {agent.last_action}")
    
    def _update_agent_needs(self, agent: Agent, time_delta: float):
        """Update agent's basic needs."""
        old_hunger = agent.hunger
        old_thirst = agent.thirst
        old_energy = agent.energy
        old_health = agent.health
        
        # Increase hunger and thirst over time
        agent.hunger = min(100.0, agent.hunger + 0.1 * time_delta)
        agent.thirst = min(100.0, agent.thirst + 0.15 * time_delta)
        
        # Decrease energy based on hunger and thirst
        energy_loss = (agent.hunger + agent.thirst) * 0.01 * time_delta
        agent.energy = max(0.0, agent.energy - energy_loss)
        
        # Decrease health if energy is too low
        if agent.energy < 20.0:
            agent.health = max(0.0, agent.health - 0.1 * time_delta)
        
        # Log significant changes
        if abs(agent.hunger - old_hunger) > 5 or abs(agent.thirst - old_thirst) > 5:
            self.logger.info(f"Agent {agent.name} needs changed - "
                           f"Hunger: {old_hunger:.1f} -> {agent.hunger:.1f}, "
                           f"Thirst: {old_thirst:.1f} -> {agent.thirst:.1f}")
        
        if abs(agent.energy - old_energy) > 10 or abs(agent.health - old_health) > 5:
            self.logger.info(f"Agent {agent.name} status changed - "
                           f"Energy: {old_energy:.1f} -> {agent.energy:.1f}, "
                           f"Health: {old_health:.1f} -> {agent.health:.1f}")
    
    def _update_agent_position(self, agent: Agent, time_delta: float):
        """Update agent's position considering terrain and energy costs."""
        old_position = agent.position
        
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
            self.logger.info(f"Agent {agent.name} is resting to recover energy. "
                           f"Current energy: {agent.energy:.1f}")
            return
        
        # Calculate possible movement range based on energy
        # Use smaller base distance (0.001 instead of 0.01)
        max_distance = min(0.001 * time_delta, agent.energy / movement_cost)
        
        # Generate random movement within energy constraints
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, max_distance)
        
        # Calculate new position
        lon, lat = agent.position
        new_lon = lon + distance * math.cos(angle)
        new_lat = lat + distance * math.sin(angle)
        
        # Try to move to new position
        if agent.move(new_lon, new_lat):
            # Update agent positions tracking
            if old_position in self.agent_positions:
                self.agent_positions[old_position].remove(agent.id)
                if not self.agent_positions[old_position]:
                    del self.agent_positions[old_position]
            
            if agent.position not in self.agent_positions:
                self.agent_positions[agent.position] = set()
            self.agent_positions[agent.position].add(agent.id)
            
            # Log movement
            self.logger.info(f"Agent {agent.name} moved from {old_position} to {agent.position}")
    
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
        slope_cost = 1.0 + (slope * 0.1)  # Reduce slope impact to allow movement
        
        return base_cost * terrain_cost * slope_cost
    
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