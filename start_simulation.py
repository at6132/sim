# import eventlet
# eventlet.monkey_patch()

import logging
import sys
import threading
import traceback
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from simulation.engine import SimulationEngine
from simulation.database import DatabaseManager
from simulation.utils.logging_config import get_logger, setup_logging
import webbrowser
import time
import os
from simulation.server import app, socketio, run_server
from simulation.routes import *  # Import all routes
from simulation.world import World
from datetime import datetime
from pathlib import Path

# Configure logging using the project's logging setup
setup_logging()
logger = get_logger(__name__)

# Initialize database
db = DatabaseManager()

# Global simulation instance
engine = None
simulation_thread = None
running = False

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)

def run_simulation_loop():
    """Main simulation loop running at 48 ticks per second, each tick is 1 second in game."""
    global engine
    try:
        last_tick_time = time.time()
        tick_interval = 1.0 / 48.0  # 48 ticks per second
        while True:
            current_time = time.time()
            elapsed = current_time - last_tick_time
            if elapsed >= tick_interval:
                if engine and engine.running:
                    # Calculate how many ticks to process
                    ticks_to_process = min(int(elapsed / tick_interval), 48)
                    for _ in range(ticks_to_process):
                        try:
                            engine.update(1)  # Each tick is 1 second in game
                        except Exception as e:
                            logger.error(f"Error in simulation tick: {e}")
                            logger.error(traceback.format_exc())
                    last_tick_time = current_time
            time.sleep(0.001)
    except Exception as e:
        logger.error(f"Error in simulation loop: {e}")
        logger.error(traceback.format_exc())

def start_backend_server():
    """Start the Flask backend server."""
    try:
        logger.info("Starting backend server...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f"Error starting backend server: {e}")
        logger.error(traceback.format_exc())

def start_frontend():
    """Start the frontend in the default web browser."""
    try:
        logger.info("Starting frontend...")
        webbrowser.open('http://localhost:5000')
    except Exception as e:
        logger.error(f"Error starting frontend: {e}")
        logger.error(traceback.format_exc())

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
        
        # Start backend server in a separate thread
        logger.info("Starting backend server...")
        server_thread = threading.Thread(target=start_backend_server, daemon=True)
        server_thread.start()
        
        # Start frontend
        start_frontend()
        
        # Main simulation loop
        last_tick_time = time.time()
        tick_interval = 1.0 / 48.0  # 48 ticks per second
        
        while True:
            try:
                current_time = time.time()
                elapsed = current_time - last_tick_time
                
                if elapsed >= tick_interval:
                    # Calculate how many ticks to process
                    ticks_to_process = min(int(elapsed / tick_interval), 48)
                    time_delta = ticks_to_process * tick_interval
                    
                    # Update world state
                    world.update(time_delta)
                    
                    # Autosave every 1000 ticks
                    if world.current_tick % 1000 == 0:
                        world._save_state()
                    
                    last_tick_time = current_time
                
                # Sleep to control simulation speed
                time.sleep(0.001)
                
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

def main():
    """Main entry point for the simulation."""
    try:
        # Create save directories if they don't exist
        os.makedirs('simulation_saves', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('data/agents', exist_ok=True)
        os.makedirs('data/animals', exist_ok=True)
        os.makedirs('data/marine', exist_ok=True)
        os.makedirs('data/world', exist_ok=True)
        os.makedirs('data/civilization', exist_ok=True)
        os.makedirs('data/events', exist_ok=True)
        
        # Initialize world
        world = World(logger)
        world.spawn_initial_agents()
        
        # Initialize engine
        engine = SimulationEngine(world, logger)
        
        # Start server
        run_server()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 