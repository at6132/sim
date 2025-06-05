from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from .utils.logging_config import get_logger

logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/api/world")
def get_world_state():
    """Get current world state."""
    from .engine import engine
    if engine and engine.world:
        return jsonify(engine.world.get_state())
    return jsonify({"error": "World not initialized"})

@app.route("/api/start")
def start_simulation():
    """Start the simulation."""
    from .engine import engine
    if engine:
        engine.start()
        return jsonify({"status": "started"})
    return jsonify({"error": "Engine not initialized"})

@app.route("/api/stop")
def stop_simulation():
    """Stop the simulation."""
    from .engine import engine
    if engine:
        engine.stop()
        return jsonify({"status": "stopped"})
    return jsonify({"error": "Engine not initialized"})

@app.route("/api/reset")
def reset_simulation():
    """Reset the simulation to initial state."""
    from .engine import engine
    if engine:
        engine.reset()
        return jsonify({"status": "reset"})
    return jsonify({"error": "Engine not initialized"})

# Export app and socketio for use in routes
__all__ = ['app', 'socketio'] 