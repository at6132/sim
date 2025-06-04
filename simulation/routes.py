from flask import jsonify, render_template
from flask_socketio import emit
import logging

logger = logging.getLogger(__name__)

# Import simulation instance from main
from .main import simulation

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")
    if simulation:
        emit('simulation_state', simulation.get_state())

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