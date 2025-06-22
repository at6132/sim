from flask import jsonify, render_template, request, Blueprint
import json
from flask_socketio import emit
import logging
from .server import app, socketio
from .engine import get_engine
from typing import Dict, List, Optional, Tuple
import random
from datetime import datetime
from .utils.logging_config import get_logger
import traceback
from .world import World

logger = get_logger(__name__)

# Create blueprint
api = Blueprint('api', __name__)

@api.route('/')
def index():
    """Render main simulation view."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect(auth=None):
    """Handle client connection."""
    try:
        engine = get_engine()
        if not engine or not engine.world:
            logger.error("Engine or world not initialized")
            return
            
        # Get current world state
        state = engine.world.get_state()
        
        # Convert any tuple keys to strings
        def convert_tuple_keys(obj):
            if isinstance(obj, dict):
                return {str(k) if isinstance(k, tuple) else k: convert_tuple_keys(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_tuple_keys(item) for item in obj]
            return obj
        
        # Convert state before sending
        state = convert_tuple_keys(state)
        
        # Send initial state
        emit('simulation_state', state)
        logger.info("Sent initial state to client")
    except Exception as e:
        logger.error(f"Error sending initial state: {e}")
        logger.error(traceback.format_exc())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected")

@api.route('/api/start', methods=['POST'])
def start_simulation():
    """Start the simulation."""
    try:
        engine = get_engine()
        if engine:
            engine.start()
            return jsonify({'status': 'started'})
        return jsonify({'error': 'Engine not initialized'}), 500
    except Exception as e:
        logger.error(f"Error starting simulation: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api.route('/api/stop', methods=['POST'])
def stop_simulation():
    """Stop the simulation."""
    try:
        engine = get_engine()
        if engine:
            engine.stop()
            return jsonify({'status': 'stopped'})
        return jsonify({'error': 'Engine not initialized'}), 500
    except Exception as e:
        logger.error(f"Error stopping simulation: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api.route('/api/reset', methods=['POST'])
def reset_simulation():
    """Reset the simulation to initial state."""
    try:
        engine = get_engine()
        if engine:
            engine.world = World()
            engine.world.spawn_initial_agents()
            return jsonify({'status': 'reset'})
        return jsonify({'error': 'Engine not initialized'}), 500
    except Exception as e:
        logger.error(f"Error resetting simulation: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api.route('/api/state', methods=['GET'])
def get_state():
    """Get current simulation state."""
    try:
        engine = get_engine()
        if engine:
            return jsonify(engine.get_state())
        return jsonify({'error': 'Engine not initialized'}), 500
    except Exception as e:
        logger.error(f"Error getting simulation state: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api.route('/api/save', methods=['POST'])
def save_state():
    """Save current simulation state."""
    try:
        data = request.get_json()
        save_name = data.get('save_name') if data else None
        
        engine = get_engine()
        if engine:
            engine.save_state(save_name)
            return jsonify({'status': 'saved'})
        return jsonify({'error': 'Engine not initialized'}), 500
    except Exception as e:
        logger.error(f"Error saving simulation state: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api.route('/api/load', methods=['POST'])
def load_state():
    """Load a saved simulation state."""
    try:
        data = request.get_json()
        if not data or 'save_name' not in data:
            return jsonify({'error': 'No save name provided'}), 400
            
        engine = get_engine()
        if engine:
            engine.load_state(data['save_name'])
            return jsonify({'status': 'loaded'})
        return jsonify({'error': 'Engine not initialized'}), 500
    except Exception as e:
        logger.error(f"Error loading simulation state: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api.route('/api/saves', methods=['GET'])
def get_saves():
    """Get list of available saves."""
    try:
        engine = get_engine()
        if engine:
            return jsonify({'saves': engine.get_save_list()})
        return jsonify({'error': 'Engine not initialized'}), 500
    except Exception as e:
        logger.error(f"Error getting save list: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/world')
def get_world():
    engine = get_engine()
    if engine and engine.world:
        # Attempt to fetch the latest state from Redis first
        if getattr(engine.world, "redis", None):
            try:
                data = engine.world.redis.get("world_state")
                if data:
                    return jsonify(json.loads(data))
            except Exception as e:
                logger.error(f"Error reading world state from Redis: {e}")
        # Fallback to in-memory state
        return jsonify(engine.world.get_state())
    return jsonify({"error": "Simulation not initialized"}), 503

@app.route('/api/agents')
def get_agents():
    engine = get_engine()
    if engine and engine.world:
        return jsonify([{
            'id': agent.id,
            'type': agent.type,
            'position': agent.position,
            'status': agent.status,
            'attributes': agent.attributes,
            'inventory': agent.inventory,
            'current_action': agent.current_action
        } for agent in engine.world.agents])
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

@api.route('/api/status')
def get_status():
    """Get current simulation status."""
    try:
        engine = get_engine()
        if engine:
            return jsonify({
                'status': 'running' if engine.running else 'stopped',
                'tick': engine.world.current_tick if engine.world else 0
            })
        return jsonify({'status': 'not_initialized'})
    except Exception as e:
        logger.error(f"Error getting simulation status: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

def broadcast_agent_updates():
    """Broadcast agent location updates to all connected clients."""
    engine = get_engine()
    if engine and engine.world:
        try:
            agent_updates = {}
            for agent_id, agent in engine.world.agents.agents.items():
                try:
                    agent_updates[str(agent_id)] = {
                        'id': str(agent_id),
                        'name': str(agent.name),
                        'position': [float(agent.position[0]), float(agent.position[1])],
                        'health': float(agent.health),
                        'energy': float(agent.energy),
                        'hunger': float(agent.hunger),
                        'thirst': float(agent.thirst),
                        'age': int(agent.age),
                        'skills': {str(k): float(v) for k, v in agent.skills.items()},
                        'inventory': {str(k): float(v) if isinstance(v, (int, float)) else str(v) for k, v in agent.inventory.items()},
                        'last_action': str(agent.last_action) if agent.last_action else None
                    }
                except Exception as e:
                    logger.error(f"Error converting agent {agent_id} to dict: {e}")
                    continue
            
            socketio.emit('agent_updates', agent_updates)
        except Exception as e:
            logger.error(f"Error broadcasting agent updates: {e}")
            logger.error(traceback.format_exc()) 