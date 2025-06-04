from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import logging

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
CORS(app)
socketio = SocketIO(app, async_mode='threading')

def start_backend():
    """Start the Flask backend server."""
    logger.info("Starting backend server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

# Export app and socketio for use in routes
__all__ = ['app', 'socketio'] 