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
from simulation.utils.logging_config import setup_logging, get_logger
import webbrowser
import time
import os
from simulation.server import start_backend

# Set up logging
logger = setup_logging(log_level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, async_mode='threading')

# Initialize database
db = DatabaseManager()

# Global simulation instance
engine = None
simulation_thread = None
running = False

def run_simulation_loop():
    """Run the main simulation loop."""
    global running
    running = True
    
    logger.info("Starting simulation loop...")
    while running:
        try:
            # Update simulation state
            engine.world.update(48.0)  # 48 minutes = 0.8 hours
            
            # Emit state to frontend
            socketio.emit('simulation_state', engine.world.to_dict())
            
            # Log progress
            logger.info(f"Simulation tick completed")
            
            # Sleep for 1 minute
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in simulation loop: {e}")
            logger.error(traceback.format_exc())
            break
    
    running = False

def start_backend():
    """Start the Flask backend server."""
    logger.info("Starting backend server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

def start_frontend():
    """Start the frontend in the default web browser."""
    logger.info("Starting frontend...")
    # Wait a moment for the backend to initialize
    time.sleep(2)
    webbrowser.open('http://localhost:5000')
    logger.info("Frontend started")

def start_simulation():
    """Main startup sequence."""
    global engine, simulation_thread
    
    try:
        # Step 1: Create simulation engine instance
        logger.info("Creating simulation engine...")
        engine = SimulationEngine()
        
        # Step 2: Start the simulation engine
        logger.info("Starting simulation engine...")
        engine.start()
        
        # Step 3: Initialize all systems
        logger.info("Initializing world systems...")
        if engine.world:
            # Initialize terrain first (required by other systems)
            engine.world.terrain.initialize_terrain()
            
            # Initialize climate (required for spawning)
            engine.world.climate.initialize_earth_climate()
            
            # Initialize resources
            engine.world.resources.initialize_resources()
            
            # Initialize plants
            engine.world.plants.initialize_plants()
            
            # Initialize animals
            engine.world.animal_system.initialize_animals()
            
            # Initialize marine life
            engine.world.marine_system.initialize_marine()
            
            # Initialize technology
            engine.world.technology.initialize_technology()
            
            # Initialize society and transportation
            engine.world.society.initialize_society()
            engine.world.transportation_system.initialize_transportation()
            
            # Create initial agents
            engine.world.spawn_initial_agents(2)
            
            logger.info("World initialization complete - All systems ready")
        
        # Step 4: Start simulation loop in a separate thread
        logger.info("Starting simulation thread...")
        simulation_thread = threading.Thread(target=run_simulation_loop)
        simulation_thread.daemon = True
        simulation_thread.start()
        
        # Step 5: Start backend server in a separate thread
        logger.info("Starting backend server...")
        backend_thread = threading.Thread(target=start_backend)
        backend_thread.daemon = True
        backend_thread.start()
        
        # Step 6: Start frontend
        logger.info("Starting frontend...")
        start_frontend()
        
    except KeyboardInterrupt:
        logger.info("\nSimulation stopped by user")
    except Exception as e:
        logger.error(f"Error in startup sequence: {str(e)}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    start_simulation() 