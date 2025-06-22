from flask import Flask, render_template, jsonify
import threading
import time
from typing import Dict, Optional
from .world import World
import logging
import traceback
from .utils.logging_config import get_logger
import json
import os
from datetime import datetime

# Get logger for this module
logger = get_logger(__name__)

app = Flask(__name__)
simulation_thread = None
is_running = False

# Global engine instance
engine = None

def get_engine():
    """Get the global engine instance."""
    return engine

def simulation_loop():
    """Main simulation loop."""
    try:
        # Initialize logger
        logger = get_logger(__name__)
        
        # Try to load existing world
        world = World.load_from_save(logger)
        if world is None:
            logger.info("No save found, creating new world")
            world = World(logger)
        
        # Initialize simulation engine
        engine = SimulationEngine(world, logger)
        
        # Main simulation loop
        while True:
            try:
                # Update world state
                world.update()
                
                # Autosave every 1000 ticks
                if world.current_tick % 1000 == 0:
                    world._save_state()
                
                # Sleep to control simulation speed
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
                logger.error(traceback.format_exc())
                # Save state on error
                world._save_state()
                time.sleep(1)  # Wait before continuing
    except Exception as e:
        logger.error(f"Critical error in simulation: {e}")
        logger.error(traceback.format_exc())
        return

@app.route("/")
def index():
    """Render main simulation view."""
    return render_template("index.html")

@app.route("/api/world")
def get_world_state():
    """Get current world state."""
    global engine
    if engine and engine.world:
        return jsonify(engine.world.get_state())
    return jsonify({"error": "World not initialized"})

@app.route("/api/start")
def start_simulation():
    """Start the simulation."""
    global simulation_thread, is_running, engine
    
    if not is_running:
        logger.info("Starting simulation...")
        simulation_thread = threading.Thread(target=simulation_loop)
        simulation_thread.start()
        return jsonify({"status": "started"})
    
    return jsonify({"status": "already_running"})

@app.route("/api/stop")
def stop_simulation():
    """Stop the simulation."""
    global is_running
    
    logger.info("Stopping simulation...")
    is_running = False
    if simulation_thread:
        simulation_thread.join()
    
    return jsonify({"status": "stopped"})

@app.route("/api/reset")
def reset_simulation():
    """Reset the simulation to initial state."""
    global engine
    logger.info("Resetting simulation...")
    engine.world = World()
    engine.world.spawn_initial_agents()
    return jsonify({"status": "reset"})

def run_simulation():
    """Initialize and run the simulation server."""
    global engine
    
    # Initialize engine if not already done
    if engine is None:
        engine = SimulationEngine()
    
    # Start the Flask server
    logger.info("Starting Flask server...")
    app.run(debug=True, use_reloader=False)

class SimulationEngine:
    def __init__(self, world: World, logger: logging.Logger):
        """Initialize the simulation engine."""
        self.world = world
        self.running = False
        self.last_update_time = time.time()
        self.simulation_thread = None
        self.logger = logger
        logger.info("Simulation engine initialized")
        
        # Create save directories if they don't exist
        os.makedirs('simulation_saves', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('data/agents', exist_ok=True)
        os.makedirs('data/animals', exist_ok=True)
        os.makedirs('data/marine', exist_ok=True)
        os.makedirs('data/world', exist_ok=True)
        os.makedirs('data/civilization', exist_ok=True)
        os.makedirs('data/events', exist_ok=True)
        
    def start(self):
        """Start the simulation engine."""
        self.running = True
        self.last_update_time = time.time()
        self.logger.info("Simulation engine started")
        
        # Start simulation loop in a separate thread
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        
    def stop(self):
        """Stop the simulation engine."""
        self.running = False
        self.logger.info("Simulation engine stopped")
        
    def _simulation_loop(self):
        """Main simulation loop running at 48Hz (48 ticks per second)"""
        while self.running:
            try:
                # Process one tick
                self.update(1)
                
                # Sleep to maintain 48Hz rate
                time.sleep(1/48)
                
            except Exception as e:
                self.logger.error(f"Error in simulation loop: {e}")
                self.logger.error(traceback.format_exc())
                time.sleep(1)  # Sleep on error to prevent CPU spinning
        
    def update(self, time_delta: float):
        """Update the simulation state. Each tick is 1 second in game."""
        if not self.running:
            return
        try:
            # Update world state
            self.world.update(1)
        except Exception as e:
            self.logger.error(f"Error updating simulation: {e}")
            self.logger.error(traceback.format_exc())
        
    def get_state(self) -> Dict:
        """Get the current simulation state."""
        def convert_coords_to_str(coords):
            if isinstance(coords, tuple):
                return f"{coords[0]},{coords[1]}"
            return coords

        def convert_dict(d):
            if isinstance(d, dict):
                return {convert_coords_to_str(k): convert_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return convert_list(d)
            elif isinstance(d, tuple):
                return convert_coords_to_str(d)
            return d

        def convert_list(l):
            if isinstance(l, list):
                return [convert_dict(item) for item in l]
            return l

        try:
            return {
                'world': convert_dict(self.world.get_state()),
                'running': self.running,
                'systems': {
                    'terrain': convert_dict(self.world.terrain.get_state()),
                    'climate': convert_dict(self.world.climate.get_state()),
                    'resources': convert_dict(self.world.resources.get_state()),
                    'plants': convert_dict(self.world.plants.get_state()),
                    'animals': convert_dict(self.world.animals.get_state()),
                    'marine': convert_dict(self.world.marine.get_state()),
                    'technology': convert_dict(self.world.technology.get_state()),
                    'society': convert_dict(self.world.society.get_state()),
                    'transportation': convert_dict(self.world.transportation.get_state()),
                    'weather': convert_dict(self.world.weather.get_state())
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting simulation state: {e}")
            self.logger.error(traceback.format_exc())
            return {'error': str(e)}

    def save_state(self, save_name: str = None):
        """Save the current simulation state."""
        try:
            if save_name is None:
                save_name = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            save_dir = os.path.join('simulation_saves', save_name)
            
            # Delete old save if it exists
            if os.path.exists(save_dir):
                import shutil
                shutil.rmtree(save_dir)
            
            os.makedirs(save_dir, exist_ok=True)
            
            # Save world state
            world_state = self.world.get_state()
            with open(os.path.join(save_dir, 'world.json'), 'w') as f:
                json.dump(world_state, f, indent=2)
            
            # Save system states
            systems = {
                'terrain': self.world.terrain.get_state(),
                'climate': self.world.climate.get_state(),
                'resources': self.world.resources.get_state(),
                'plants': self.world.plants.get_state(),
                'animals': self.world.animals.get_state(),
                'marine': self.world.marine.get_state(),
                'technology': self.world.technology.get_state(),
                'society': self.world.society.get_state(),
                'transportation': self.world.transportation.get_state(),
                'weather': self.world.weather.get_state()
            }
            
            with open(os.path.join(save_dir, 'systems.json'), 'w') as f:
                json.dump(systems, f, indent=2)
                
            self.logger.info(f"Saved simulation state to {save_dir}")
            
        except Exception as e:
            self.logger.error(f"Error saving simulation state: {e}")
            self.logger.error(traceback.format_exc())
            
    def load_state(self, save_name: str):
        """Load a saved simulation state."""
        try:
            save_dir = os.path.join('simulation_saves', save_name)
            
            # Load world state
            with open(os.path.join(save_dir, 'world.json'), 'r') as f:
                world_state = json.load(f)
            self.world.load_state(world_state)
            
            # Load system states
            with open(os.path.join(save_dir, 'systems.json'), 'r') as f:
                systems = json.load(f)
                
            self.world.terrain.load_state(systems['terrain'])
            self.world.climate.load_state(systems['climate'])
            self.world.resources.load_state(systems['resources'])
            self.world.plants.load_state(systems['plants'])
            self.world.animals.load_state(systems['animals'])
            self.world.marine.load_state(systems['marine'])
            self.world.technology.load_state(systems['technology'])
            self.world.society.load_state(systems['society'])
            self.world.transportation.load_state(systems['transportation'])
            self.world.weather.load_state(systems['weather'])
            
            self.logger.info(f"Loaded simulation state from {save_dir}")
            
        except Exception as e:
            self.logger.error(f"Error loading simulation state: {e}")
            self.logger.error(traceback.format_exc())
            
    def get_save_list(self):
        """Get list of available saves."""
        try:
            saves = []
            for save_name in os.listdir('simulation_saves'):
                save_path = os.path.join('simulation_saves', save_name)
                if os.path.isdir(save_path):
                    saves.append(save_name)
            return saves
        except Exception as e:
            self.logger.error(f"Error getting save list: {e}")
            self.logger.error(traceback.format_exc())
            return []
