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
import os
import pickle
from .engine import SimulationEngine
from .utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

class Simulation:
    def __init__(self, config: Dict = None):
        self.logger = get_logger(__name__)
        self.config = config or {}
        self.save_dir = "simulation_saves"
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Initialize time tracking
        self.tick_rate = self.config.get('tick_rate', 1.0)  # seconds per tick
        self.last_tick = time.time()
        self.running = False
        self.current_tick = 0
        self.simulation_time = 0
        
        # Initialize agents
        self.agents = {}
        
        # Try to load existing world first
        self.logger.info("Attempting to load existing world...")
        self.world = World.load_from_save()
        if not self.world:
            self.logger.info("No saved world found, creating new world...")
            self.world = World()
            
        self.logger.info("Simulation initialization complete")
        
    def update(self) -> None:
        """Update simulation state"""
        if not self.running:
            return
            
        current_time = time.time()
        time_delta = current_time - self.last_tick
        
        # Update world state (48 minutes per iteration)
        self.logger.info(f"Updating world state (tick {self.current_tick})...")
        self.world.update(48.0)  # 48 minutes = 0.8 hours
        
        # Update simulation time
        self.simulation_time += time_delta
        self.current_tick += 1
        self.last_tick = current_time
        
        # Save state periodically (every hour of simulation time)
        if self.current_tick % 3600 == 0:
            self.logger.info("Saving world state...")
            self.world._save_state()
        
        # Print events from the last tick
        if self.world.events:
            for event in self.world.events[-5:]:  # Show last 5 events
                self.logger.info(f"[{event['world_time']:.1f}h] {event['type']}: {json.dumps(event['data'])}")
        
        if self.current_tick % 100 == 0:  # Log every 100 ticks
            self.logger.info(f"Simulation tick {self.current_tick} completed")
            
    def get_state(self) -> Dict:
        """Get current simulation state."""
        return {
            "tick": self.current_tick,
            "simulation_time": self.simulation_time,
            "running": self.running,
            "world": self.world.to_dict()
        }
        
    def start(self):
        """Start the simulation."""
        self.logger.info("Starting simulation...")
        self.running = True
        self.start_time = datetime.now()
        self.logger.info(f"Simulation started with {len(self.world.agents)} agents")
        
    def stop(self):
        """Stop the simulation."""
        self.logger.info("Stopping simulation...")
        self.running = False
        # Save final state
        self.logger.info("Saving final world state...")
        self.world._save_state()

def main():
    """Main entry point for the simulation."""
    # Create and start the simulation engine
    engine = SimulationEngine()
    engine.start()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
        engine.stop()

if __name__ == "__main__":
    main() 