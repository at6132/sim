from flask import Flask, render_template, jsonify
import threading
import time
from typing import Dict
from .world import World
import logging
import traceback

# Get logger for this module
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Try to load a saved world state first; if none exists, create a new World
world = World.load_from_save() or World()
simulation_thread = None
is_running = False

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
        self.running = False
        self.world = None
        self.last_update = time.time()
        self.update_interval = 1.0  # seconds
        self.simulation_speed = 1.0  # time multiplier
        self.thread = None
        logger.info("SimulationEngine initialized")
        
    def start(self):
        """Start the simulation."""
        if self.running:
            logger.warning("Simulation already running")
            return
            
        # Try to load existing world first
        logger.info("Attempting to load existing world...")
        self.world = World.load_from_save()
        if not self.world:
            logger.info("No saved world found, creating new world...")
            self.world = World()
            
        self.running = True
        self.last_update = time.time()
        
        # Start simulation in a separate thread
        self.thread = threading.Thread(target=self.run_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Simulation started in background thread")

    def update(self, time_step=48.0):
        """Advance the simulation by a given time step (in minutes)."""
        if not self.running or not self.world:
            logger.warning("SimulationEngine.update() called while not running or world is None")
            return
            
        try:
            logger.info(f"Updating simulation by {time_step} minutes...")
            self.world.update(time_step)
            self.last_update = time.time()
            logger.info("Simulation update complete")
        except Exception as e:
            logger.error(f"Error during simulation update: {e}")
            logger.error(traceback.format_exc())
            self.stop()

    def stop(self):
        """Stop the simulation."""
        if not self.running:
            logger.info("Simulation already stopped")
            return
            
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            if self.thread.is_alive():
                logger.warning("Simulation thread did not stop gracefully")
        logger.info("Simulation stopped")

    def run_loop(self, time_step=48.0, real_time_interval=60.0):
        """Run the simulation update loop until stopped."""
        logger.info("Starting simulation engine loop...")
        while self.running:
            try:
                self.update(time_step)
                time.sleep(real_time_interval)
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
                logger.error(traceback.format_exc())
                self.running = False
                break
        logger.info("Simulation engine loop exited")

    def get_state(self):
        """Get current simulation state."""
        if not self.world:
            return {"status": "not_initialized"}
        return {
            "status": "running" if self.running else "stopped",
            "world": self.world.to_dict(),
            "last_update": self.last_update,
            "simulation_speed": self.simulation_speed
        }
