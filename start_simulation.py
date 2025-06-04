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
from simulation.server import app, socketio
from simulation.routes import *  # Import all routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simulation.log')
    ]
)

logger = logging.getLogger(__name__)

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
    """Start the frontend in a web browser."""
    logger.info("Starting frontend...")
    # Wait for backend to initialize
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """Main entry point for the simulation."""
    global engine
    try:
        # Initialize simulation engine
        logger.info("Initializing simulation engine...")
        engine = SimulationEngine()
        
        # Start the engine
        logger.info("Starting simulation engine...")
        engine.start()
        
        # Start backend server in a separate thread
        logger.info("Starting backend server...")
        server_thread = threading.Thread(target=start_backend, daemon=True)
        server_thread.start()
        
        # Start frontend
        start_frontend()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down simulation...")
        if engine:
            engine.stop()
    except Exception as e:
        logger.error(f"Error in simulation: {str(e)}")
        raise

if __name__ == "__main__":
    main() 