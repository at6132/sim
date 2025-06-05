from flask import jsonify, render_template
from flask_socketio import emit
import logging
from .server import app, socketio
from .engine import get_engine
from typing import Dict, List, Optional, Tuple
import random
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@app.route('/')
def index():
    """Render main simulation view."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected")
    engine = get_engine()
    if engine and engine.world:
        emit('simulation_state', engine.get_state())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected")

@socketio.on('start_simulation')
def handle_start():
    """Handle simulation start request."""
    engine = get_engine()
    if engine:
        engine.start()
        return {"status": "started"}
    return {"error": "Engine not initialized"}

@socketio.on('stop_simulation')
def handle_stop():
    """Handle simulation stop request."""
    engine = get_engine()
    if engine:
        engine.stop()
        return {"status": "stopped"}
    return {"error": "Engine not initialized"}

@app.route('/api/world')
def get_world():
    engine = get_engine()
    if engine and engine.world:
        return jsonify(engine.world.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/agents')
def get_agents():
    engine = get_engine()
    if engine and engine.world:
        return jsonify([agent.get_state() for agent in engine.world.agents])
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/marine')
def get_marine():
    engine = get_engine()
    if engine and engine.world:
        return jsonify(engine.world.marine_system.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/plants')
def get_plants():
    engine = get_engine()
    if engine and engine.world:
        return jsonify(engine.world.plants.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/climate')
def get_climate():
    engine = get_engine()
    if engine and engine.world:
        return jsonify(engine.world.climate.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/terrain')
def get_terrain():
    engine = get_engine()
    if engine and engine.world:
        return jsonify(engine.world.terrain.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/civilization')
def get_civilization():
    engine = get_engine()
    if engine and engine.world:
        return jsonify({
            "inventions": engine.world.technology.discoveries,
            "religions": engine.world.society.religions,
            "languages": engine.world.society.languages,
            "settlements": engine.world.settlements
        })
    return jsonify({"error": "Simulation not initialized"}), 503 