import eventlet
eventlet.monkey_patch()

import logging
import sys
import threading
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from simulation.main import Simulation
from simulation.world import World
from simulation.database import DatabaseManager
import json
from datetime import datetime
import time
import random

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('simulation.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, async_mode='eventlet')

# Initialize database
db = DatabaseManager()

# Global simulation instance
simulation = None
simulation_thread = None
running = False
time_scale = 1.0  # 1 real second = 1 game hour

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")
    if simulation:
        socketio.emit('simulation_state', simulation.get_state())

def initialize_world():
    """Initialize the world with Adam, Eve, animals, and sea creatures."""
    global simulation
    
    logger.info("Initializing world...")
    
    # Create simulation with initial configuration
    config = {
        'tick_rate': 1.0,
        'initial_agents': [
            {
                'id': 'adam',
                'name': 'Adam',
                'longitude': 0.0,
                'latitude': 0.0,
                'age': 25.0,
                'gender': 'male'
            },
            {
                'id': 'eve',
                'name': 'Eve',
                'longitude': 0.1,
                'latitude': 0.1,
                'age': 25.0,
                'gender': 'female'
            }
        ]
    }
    
    simulation = Simulation(config)
    
    # Initialize database with initial state
    db.save_world_state(simulation.world.get_state())
    
    # Spawn animals across continents
    logger.info("Spawning 2000 animals across continents...")
    for _ in range(2000):
        # Get random valid land coordinates
        lon = random.uniform(-180, 180)
        lat = random.uniform(-90, 90)
        while simulation.world.get_terrain_at(lon, lat).is_water:
            lon = random.uniform(-180, 180)
            lat = random.uniform(-90, 90)
        
        simulation.animal_system.spawn_animal(
            longitude=lon,
            latitude=lat,
            species=random.choice(simulation.animal_system.available_species)
        )
    
    # Spawn sea creatures
    logger.info("Spawning 10000 sea creatures across oceans...")
    for _ in range(10000):
        # Get random valid ocean coordinates
        lon = random.uniform(-180, 180)
        lat = random.uniform(-90, 90)
        while not simulation.world.get_terrain_at(lon, lat).is_water:
            lon = random.uniform(-180, 180)
            lat = random.uniform(-90, 90)
        
        simulation.marine_system.spawn_creature(
            longitude=lon,
            latitude=lat,
            species=random.choice(simulation.marine_system.available_species)
        )
    
    logger.info("World initialization complete")
    return simulation

def run_simulation():
    """Run the simulation in a separate thread."""
    global running
    tick_count = 0
    
    try:
        while running:
            try:
                simulation.update()
                tick_count += 1
                
                # Save world state periodically
                if tick_count % 10 == 0:  # Save every 10 ticks
                    db.save_world_state(simulation.world.get_state())
                    
                    # Save agent states
                    for agent_id, agent in simulation.world.agents.items():
                        db.save_agent(agent_id, simulation.world.get_agent_json(agent_id))
                    
                    # Save animal states
                    for animal_id, animal in simulation.world.animals.animals.items():
                        db.save_animal(animal_id, simulation.world.get_animal_json(animal_id))
                    
                    # Save marine creature states
                    for creature_id, creature in simulation.world.marine.creatures.items():
                        db.save_marine_creature(creature_id, simulation.world.get_marine_creature_json(creature_id))
                    
                    # Save civilization data
                    db.save_civilization_data({
                        "inventions": simulation.world.technology.discoveries,
                        "religions": simulation.world.society.religions,
                        "languages": simulation.world.society.languages,
                        "settlements": simulation.world.settlements
                    })
                
                # Emit state updates
                state = simulation.get_state()
                socketio.emit('simulation_state', state)
                
                # Emit all events with proper formatting
                for event in simulation.world.events[-50:]:  # Last 50 events
                    formatted_event = {
                        'type': event['type'],
                        'timestamp': event['timestamp'],
                        'data': event['data']
                    }
                    socketio.emit('simulation_event', formatted_event)
                    
                    # Log events to console
                    logger.info(f"[{event['world_time']:.1f}h] {event['type']}: {json.dumps(event['data'])}")
                
                # Log every 100 ticks
                if tick_count % 100 == 0:
                    logger.info(f"Simulation tick: {tick_count}")
                    logger.info(f"Number of agents: {len(simulation.world.agents)}")
                    logger.info(f"Number of animals: {len(simulation.world.animals.animals)}")
                    
                    # Log some agent stats
                    for agent_id, agent in list(simulation.world.agents.items())[:3]:  # Log first 3 agents
                        logger.info(f"Agent {agent.name} (ID: {agent_id}):")
                        logger.info(f"  Age: {agent.age:.1f}, Health: {agent.health:.2f}")
                        logger.info(f"  Position: ({agent.longitude:.2f}, {agent.latitude:.2f})")
                        logger.info(f"  Needs - Food: {agent.needs.food:.2f}, Water: {agent.needs.water:.2f}")
                    
                    # Log civilization progress
                    logger.info("Civilization Progress:")
                    logger.info(f"  Inventions: {len(simulation.world.technology.discoveries)}")
                    logger.info(f"  Religions: {len(simulation.world.society.religions)}")
                    logger.info(f"  Languages: {len(simulation.world.society.languages)}")
                
                time.sleep(0.1)  # Prevent CPU overload
                
            except Exception as e:
                logger.error(f"Error in simulation update: {str(e)}")
                socketio.emit('simulation_error', {'error': str(e)})
                time.sleep(1)  # Prevent tight error loop
    except Exception as e:
        logger.error(f"Fatal simulation error: {str(e)}")
        running = False
        socketio.emit('simulation_error', {'error': f"Fatal error: {str(e)}"})

# API Endpoints
@app.route('/api/world/state')
def get_world_state():
    if simulation is None:
        # Try to load from database if simulation not running
        state = db.load_world_state()
        if state:
            return jsonify(state)
        return jsonify({"error": "Simulation not started"}), 503
    return jsonify(simulation.get_state())

@app.route('/api/world/reset', methods=['POST'])
def reset_world():
    global simulation, running
    logger.info("Resetting world...")
    running = False
    if simulation_thread:
        simulation_thread.join()
    simulation = initialize_world()
    return jsonify({"status": "success"})

@app.route('/api/world/timescale', methods=['POST'])
def set_time_scale():
    global time_scale
    data = request.get_json()
    new_scale = float(data.get('scale', 1.0))
    logger.info(f"Changing time scale from {time_scale} to {new_scale}")
    time_scale = new_scale
    return jsonify({"status": "success", "time_scale": time_scale})

@app.route('/api/agents')
def get_agents():
    if simulation is None:
        # Try to load from database if simulation not running
        return jsonify(db.get_all_agents())
    return jsonify({
        agent_id: simulation.world.get_agent_json(agent_id)
        for agent_id in simulation.world.agents
    })

@app.route('/api/agent/<agent_id>')
def get_agent(agent_id):
    if simulation is None:
        # Try to load from database if simulation not running
        agent_data = db.load_agent(agent_id)
        if agent_data:
            return jsonify(agent_data)
        return jsonify({"error": "Agent not found"}), 404
    
    if agent_id not in simulation.world.agents:
        return jsonify({"error": "Agent not found"}), 404
    return jsonify(simulation.world.get_agent_json(agent_id))

@app.route('/api/animals')
def get_animals():
    if simulation is None:
        # Try to load from database if simulation not running
        return jsonify(db.get_all_animals())
    return jsonify({
        animal_id: simulation.world.get_animal_json(animal_id)
        for animal_id in simulation.world.animals.animals
    })

@app.route('/api/marine')
def get_marine_creatures():
    if simulation is None:
        # Try to load from database if simulation not running
        return jsonify(db.get_all_marine_creatures())
    return jsonify({
        creature_id: simulation.world.get_marine_creature_json(creature_id)
        for creature_id in simulation.world.marine.creatures
    })

@app.route('/api/civilization')
def get_civilization():
    if simulation is None:
        # Try to load from database if simulation not running
        civ_data = db.load_civilization_data()
        if civ_data:
            return jsonify(civ_data)
        return jsonify({"error": "No civilization data available"}), 503
    
    return jsonify({
        "inventions": simulation.world.technology.discoveries,
        "religions": simulation.world.society.religions,
        "languages": simulation.world.society.languages,
        "settlements": simulation.world.settlements
    })

@app.route('/api/events')
def get_events():
    limit = request.args.get('limit', default=100, type=int)
    return jsonify(db.get_recent_events(limit))

def start_simulation():
    """Start the simulation and web interface."""
    global running, simulation_thread
    
    logger.info("Starting simulation system...")
    
    # Initialize world
    simulation = initialize_world()
    
    # Start simulation thread
    running = True
    simulation_thread = threading.Thread(target=run_simulation)
    simulation_thread.start()
    
    # Start web interface
    logger.info("Starting web interface on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    start_simulation() 