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

# Configure logging using the project's logging setup
setup_logging()
logger = get_logger(__name__)

# Initialize database
db = DatabaseManager()

# Global simulation instance
engine = None
simulation_thread = None
running = False

def run_simulation_loop():
    """Main simulation loop running at 48 ticks per second."""
    try:
        while True:
            if engine.running:
                # Run 48 ticks per second, each tick representing 1 game second
                for _ in range(48):
                    engine.world.update(1/48)  # Each tick is 1/48th of a second
            time.sleep(0.001)  # Small sleep to prevent CPU overload
    except Exception as e:
        logger.error(f"Error in simulation loop: {e}")
        logger.error(traceback.format_exc())

def start_backend_server():
    """Start the Flask backend server."""
    logger.info("Starting backend server...")
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)

def start_frontend():
    """Start the frontend interface."""
    logger.info("Starting frontend...")
    time.sleep(2)  # Give the server time to start
    webbrowser.open('http://localhost:5001')

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
        server_thread = threading.Thread(target=start_backend_server, daemon=True)
        server_thread.start()
        
        # Start simulation loop in a separate thread
        logger.info("Starting simulation loop...")
        simulation_thread = threading.Thread(target=run_simulation_loop, daemon=True)
        simulation_thread.start()
        
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