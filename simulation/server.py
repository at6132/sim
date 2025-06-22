from flask import Flask, render_template
from flask_socketio import SocketIO
from .engine import SimulationEngine, get_engine
from .world import World
from .utils.logging_config import get_logger
import logging
import traceback
import threading
import time

# Get logger for this module
logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes after app is created
from .routes import api

# Register blueprint
app.register_blueprint(api)

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected")

def run_server():
    """Run the Flask server."""
    try:
        logger.info("Starting Flask server...")
        socketio.run(app, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Error running server: {e}")
        logger.error(traceback.format_exc()) 