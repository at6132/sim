from flask import jsonify, render_template
from flask_socketio import emit
import logging
from .server import app, socketio
from .engine import engine

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Render main simulation view."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected")
    if engine and engine.world:
        emit('simulation_state', engine.get_state())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected")

@socketio.on('start_simulation')
def handle_start():
    """Handle simulation start request."""
    if engine:
        engine.start()
        return {"status": "started"}
    return {"error": "Engine not initialized"}

@socketio.on('stop_simulation')
def handle_stop():
    """Handle simulation stop request."""
    if engine:
        engine.stop()
        return {"status": "stopped"}
    return {"error": "Engine not initialized"}

@app.route('/api/world')
def get_world():
    if engine and engine.world:
        return jsonify(engine.world.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/agents')
def get_agents():
    if engine and engine.world:
        return jsonify([agent.get_state() for agent in engine.world.agents])
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/marine')
def get_marine():
    if engine and engine.world:
        return jsonify(engine.world.marine_system.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/plants')
def get_plants():
    if engine and engine.world:
        return jsonify(engine.world.plants.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/climate')
def get_climate():
    if engine and engine.world:
        return jsonify(engine.world.climate.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/terrain')
def get_terrain():
    if engine and engine.world:
        return jsonify(engine.world.terrain.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/civilization')
def get_civilization():
    if engine and engine.world:
        return jsonify({
            "inventions": engine.world.technology.discoveries,
            "religions": engine.world.society.religions,
            "languages": engine.world.society.languages,
            "settlements": engine.world.settlements
        })
    return jsonify({"error": "Simulation not initialized"}), 503 