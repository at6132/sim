import logging
import time
from datetime import datetime
import json
from typing import Dict, List, Optional
from .world import World
from .utils.logging_config import get_logger
import os

# Get logger for this module
logger = get_logger(__name__)

class Simulation:
    def __init__(self, config: Dict = None):
        """Initialize simulation with optional configuration."""
        self.logger = get_logger(__name__)
        self.config = config or {}
        self.save_dir = "simulation_saves"
        os.makedirs(self.save_dir, exist_ok=True)
        self.tick_rate = self.config.get('tick_rate', 1.0)
        self.last_tick = time.time()
        self.running = False
        self.current_tick = 0
        self.simulation_time = 0
        self.logger.info("Attempting to load existing world...")
        self.world = World.load_from_save()
        if not self.world:
            self.logger.info("No saved world found, creating new world...")
            self.world = World()
        self.logger.info("Simulation initialization complete")
    def update(self, time_delta: float) -> None:
        """Update simulation state"""
        if not self.running:
            return
        self.world.update(1)
        self.simulation_time += 1
        self.current_tick += 1
        # Print events from the last tick
        if self.world.events:
            for event in self.world.events[-5:]:
                self.logger.info(f"[{event['world_time']:.1f}h] {event['type']}: {json.dumps(event['data'])}")
        if self.current_tick % 100 == 0:
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
        self.logger.info(f"Simulation started with {len(self.world.agents.agents)} agents")
    def stop(self):
        """Stop the simulation."""
        self.logger.info("Stopping simulation...")
        self.running = False
        self.logger.info("Saving final world state...")
        self.world._save_state() 