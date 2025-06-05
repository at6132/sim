from typing import Dict, List, Optional, Set, Tuple
import uuid
import time
from datetime import datetime
from .utils.logging_config import get_logger

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
        
        # Create a small group of initial agents
        initial_positions = [
            (0, 0),  # First agent at origin
            (0.1, 0.1),  # Second agent nearby
            (-0.1, -0.1)  # Third agent nearby
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
        """Update agent's position."""
        # Simple random movement for now
        import random
        lon, lat = agent.position
        lon += random.uniform(-0.01, 0.01) * time_delta
        lat += random.uniform(-0.01, 0.01) * time_delta
        
        # Ensure position is within world bounds
        lon = max(self.world.min_longitude, min(self.world.max_longitude, lon))
        lat = max(self.world.min_latitude, min(self.world.max_latitude, lat))
        
        # Update position
        old_position = agent.position
        agent.position = (lon, lat)
        
        # Update position tracking
        if old_position in self.agent_positions:
            self.agent_positions[old_position].remove(agent.id)
            if not self.agent_positions[old_position]:
                del self.agent_positions[old_position]
        
        if agent.position not in self.agent_positions:
            self.agent_positions[agent.position] = set()
        self.agent_positions[agent.position].add(agent.id)
    
    def _update_agent_skills(self, agent: Agent, time_delta: float):
        """Update agent's skills."""
        # Skills improve slightly over time
        for skill in agent.skills:
            improvement = 0.001 * time_delta
            agent.skills[skill] = min(1.0, agent.skills[skill] + improvement)
    
    def _update_agent_inventory(self, agent: Agent, time_delta: float):
        """Update agent's inventory."""
        # Consume food and water
        if agent.hunger > 50.0 and 'food' in agent.inventory:
            agent.inventory['food'] = max(0.0, agent.inventory['food'] - 0.1 * time_delta)
            agent.hunger = max(0.0, agent.hunger - 0.2 * time_delta)
        
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
                    'last_update': agent.last_update
                }
                for agent_id, agent in self.agents.items()
            },
            'agent_positions': {
                str(pos): list(agent_ids)
                for pos, agent_ids in self.agent_positions.items()
            }
        } 