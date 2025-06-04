from flask import jsonify, render_template
from flask_socketio import emit
import logging
from .server import app, socketio

logger = logging.getLogger(__name__)

# Import simulation instance from main
from .main import simulation

@app.route('/')
def index():
    """Render main simulation view."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected")
    if simulation:
        emit('simulation_state', simulation.get_state())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected")

@socketio.on('start_simulation')
def handle_start():
    """Handle simulation start request."""
    from .engine import engine
    if engine:
        engine.start()
        return {"status": "started"}
    return {"error": "Engine not initialized"}

@socketio.on('stop_simulation')
def handle_stop():
    """Handle simulation stop request."""
    from .engine import engine
    if engine:
        engine.stop()
        return {"status": "stopped"}
    return {"error": "Engine not initialized"}

@app.route('/api/world')
def get_world():
    if simulation is None:
        return jsonify({"error": "Simulation not initialized"}), 503
    return jsonify(simulation.world.get_state())

@app.route('/api/agents')
def get_agents():
    if simulation is None:
        return jsonify({"error": "Simulation not initialized"}), 503
    return jsonify([agent.get_state() for agent in simulation.agents.values()])

@app.route('/api/marine')
def get_marine():
    if simulation is None:
        return jsonify({"error": "Simulation not initialized"}), 503
    return jsonify(simulation.world.marine.get_state())

@app.route('/api/plants')
def get_plants():
    if simulation is None:
        return jsonify({"error": "Simulation not initialized"}), 503
    return jsonify(simulation.world.plants.get_state())

@app.route('/api/climate')
def get_climate():
    if simulation is None:
        return jsonify({"error": "Simulation not initialized"}), 503
    return jsonify(simulation.world.climate.get_state())

@app.route('/api/terrain')
def get_terrain():
    if simulation is None:
        return jsonify({"error": "Simulation not initialized"}), 503
    return jsonify(simulation.world.terrain.get_state())

@app.route('/api/civilization')
def get_civilization():
    if simulation is None:
        return jsonify({"error": "Simulation not initialized"}), 503
    return jsonify({
        "inventions": simulation.world.technology.discoveries,
        "religions": simulation.world.society.religions,
        "languages": simulation.world.society.languages,
        "settlements": simulation.world.settlements
    }) 