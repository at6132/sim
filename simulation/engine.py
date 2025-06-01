from flask import Flask, render_template, jsonify
import threading
import time
from typing import Dict
from .world import World

app = Flask(__name__)
world = World()
simulation_thread = None
is_running = False

def simulation_loop():
    """Main simulation loop."""
    global is_running
    is_running = True
    
    while is_running:
        # Update world state (1 hour per iteration)
        world.update(1.0)
        
        # Sleep to maintain real-time ratio (1 hour = 2 days)
        # 1 hour = 3600 seconds, so we sleep for 3600/48 = 75 seconds
        time.sleep(75)

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
        simulation_thread = threading.Thread(target=simulation_loop)
        simulation_thread.start()
        return jsonify({"status": "started"})
    
    return jsonify({"status": "already_running"})

@app.route("/api/stop")
def stop_simulation():
    """Stop the simulation."""
    global is_running
    
    is_running = False
    if simulation_thread:
        simulation_thread.join()
    
    return jsonify({"status": "stopped"})

@app.route("/api/reset")
def reset_simulation():
    """Reset the simulation to initial state."""
    global world
    world = World()
    world.spawn_initial_agents()
    return jsonify({"status": "reset"})

def run_simulation():
    """Initialize and run the simulation server."""
    # Spawn initial agents
    world.spawn_initial_agents()
    
    # Start the Flask server
    app.run(debug=True, use_reloader=False)
