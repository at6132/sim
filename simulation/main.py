import logging
import time
from datetime import datetime
import json
from typing import Dict, List, Optional
from .world import World
from .agent import Agent
from .life_cycle import LifeCycleSystem
from .cognition import CognitiveSystem
from .emotions import EmotionSystem
from .philosophy import Philosophy
from .animal import AnimalSystem
from .plants import PlantSystem
from .weather import WeatherSystem
from .technology import TechnologySystem
from .resources import ResourceSystem
from .tribe import TribeSystem
from .marine import MarineSystem
import random

class Simulation:
    def __init__(self, config: Dict):
        self.logger = logging.getLogger(__name__)
        # Initialize world
        self.world = World()
        self.logger.info("Initialized world with longitude/latitude coordinates")
        
        # Initialize systems
        self.animal_system = AnimalSystem(self.world)
        self.plant_system = PlantSystem(self.world)
        self.weather_system = WeatherSystem(self.world)
        self.marine_system = MarineSystem(self.world)
        
        # Initialize time tracking
        self.tick_rate = config.get('tick_rate', 1.0)  # seconds per tick
        self.last_tick = time.time()
        self.running = False
        self.current_tick = 0
        self.simulation_time = 0
        
        # Initialize agents
        self.agents = {}
        for agent_config in config.get('initial_agents', []):
            self.add_agent(agent_config)
        
        # Initialize systems
        self.logger.info("Initializing simulation systems...")
        self._initialize_systems()
        self.logger.info("Simulation initialization complete")
        
    def update(self) -> None:
        """Update simulation state"""
        current_time = time.time()
        time_delta = (current_time - self.last_tick) * self.tick_rate
        self.last_tick = current_time
        
        # Update world state
        self.world.update(time_delta)
        
        # Update systems
        self.animal_system.update(time_delta)
        self.plant_system.update(time_delta)
        self.weather_system.update(time_delta)
        self.marine_system.update(time_delta)
        
        # Update agents
        for agent in self.agents.values():
            agent.update(time_delta)
            
        self.current_tick += 1
        self.simulation_time += time_delta
        
        # Print events from the last tick
        if self.world.events:
            for event in self.world.events[-5:]:  # Show last 5 events
                self.logger.info(f"[{event['world_time']:.1f}h] {event['type']}: {json.dumps(event['data'])}")
        
        if self.current_tick % 100 == 0:  # Log every 100 ticks
            self.logger.info(f"Simulation tick {self.current_tick} completed")
            
    def get_world_state(self) -> Dict:
        """Get current world state"""
        return {
            "environment": self.world.get_environment_state(),
            "agents": {agent_id: agent.get_state() for agent_id, agent in self.agents.items()},
            "time": {
                "real": self.world.real_time_start.isoformat(),
                "game": self.world.game_time_start.isoformat(),
                "scale": self.world.time_scale
            }
        }

    def start(self):
        """Start the simulation."""
        self.logger.info("Starting simulation...")
        self.running = True
        self.start_time = datetime.now()
        
        # Spawn initial agents if not already done
        if not self.world.agents:
            self.logger.info("Spawning initial agents...")
            self._initialize_systems()
        
        self.logger.info(f"Simulation started with {len(self.world.agents)} agents")
        
    def stop(self):
        """Stop the simulation."""
        self.logger.info("Stopping simulation...")
        self.running = False
        
    def _initialize_systems(self):
        """Initialize all simulation systems."""
        self.logger.info("Initializing simulation systems...")
        
        # Initialize world systems
        self.world._initialize_world()
        
        # Spawn initial animals
        self._spawn_initial_animals()
        
        self.logger.info("All systems initialized")
        
    def _spawn_initial_animals(self):
        """Spawn initial animals in the world."""
        self.logger.info("Spawning initial animals...")
        self.animal_system.spawn_initial_animals()
        
    def add_agent(self, agent_config: Dict):
        """Add a new agent to the simulation."""
        agent_id = agent_config.get('id')
        if agent_id in self.agents:
            self.logger.warning(f"Agent {agent_id} already exists")
            return
            
        agent = Agent(
            id=agent_id,
            name=agent_config.get('name', f"Agent {agent_id}"),
            longitude=agent_config.get('longitude', -75.0),  # Default to NYC
            latitude=agent_config.get('latitude', 40.7128)
        )
        
        self.agents[agent_id] = agent
        self.logger.info(f"Added agent {agent.name} (ID: {agent_id}) at coordinates ({agent.longitude}, {agent.latitude})")
        
    def get_state(self) -> Dict:
        """Get current simulation state."""
        return {
            "tick": self.current_tick,
            "simulation_time": self.simulation_time,
            "running": self.running,
            "world": self.world.to_dict()
        } 