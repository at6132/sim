from flask import Flask, render_template, jsonify
import threading
import time
from typing import Dict, Optional
from .world import World
import logging
import traceback
from .utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

app = Flask(__name__)
# Try to load a saved world state first; if none exists, create a new World
world = World.load_from_save() or World()
simulation_thread = None
is_running = False

# Global engine instance
engine = None

def get_engine():
    """Get the global engine instance."""
    return engine

def simulation_loop():
    """Main simulation loop."""
    global is_running
    is_running = True
    
    logger.info("Starting simulation loop...")
    while is_running:
        try:
            # Update world state (48 minutes per iteration)
            logger.info("Updating world state...")
            world.update(48.0)  # 48 minutes = 0.8 hours
            
            # Sleep to maintain real-time ratio (1 minute real time = 48 minutes game time)
            time.sleep(60)  # Sleep for 1 minute
            logger.info("Simulation tick completed")
            
        except Exception as e:
            logger.error(f"Error in simulation loop: {e}")
            logger.error(traceback.format_exc())
            break

@app.route("/")
def index():
    """Render main simulation view."""
    return render_template("index.html")

@app.route("/api/world")
def get_world_state():
    """Get current world state."""
    return jsonify(world.to_dict())

@app.route("/api/start")
def start_simulation():
    """Start the simulation."""
    global simulation_thread, is_running
    
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
    global world
    logger.info("Resetting simulation...")
    world = World()
    world.spawn_initial_agents()
    return jsonify({"status": "reset"})

def run_simulation():
    """Initialize and run the simulation server."""
    # Spawn initial agents
    logger.info("Spawning initial agents...")
    world.spawn_initial_agents()
    
    # Start the Flask server
    logger.info("Starting Flask server...")
    app.run(debug=True, use_reloader=False)

class SimulationEngine:
    def __init__(self):
        """Initialize the simulation engine."""
        global engine
        self.world = World()
        self.running = False
        engine = self  # Set global instance
        logger.info("Simulation engine initialized")
        
    def start(self):
        """Start the simulation engine."""
        self.running = True
        logger.info("Simulation engine started")
        
    def stop(self):
        """Stop the simulation engine."""
        self.running = False
        logger.info("Simulation engine stopped")
        
    def update(self, time_delta: float):
        """Update the simulation state."""
        if not self.running:
            return
            
        self.world.update(time_delta)
        
    def get_state(self) -> Dict:
        """Get the current simulation state."""
        return {
            'world': self.world.get_state(),
            'running': self.running
        }
