# World Simulation

A complex world simulation system that models various aspects of Earth-like environments, including climate, terrain, resources, and civilization development.

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Ensure a Redis server is running locally (or set `REDIS_HOST` and `REDIS_PORT`)
so the simulation can persist world state for the frontend.

The simulation runs at a time scale of **48×**, meaning one in-game day
passes every 30 minutes of real time.

## Running the Simulation

1. Launch the dashboard:
```bash
python run_dashboard.py
```

This will:
- Initialize the simulation engine
- Start the backend server
- Persist each tick to Redis
- Open the God view dashboard in your web browser

2. Access the simulation:
- Frontend: http://localhost:5000
- API endpoints:
  - /api/world - Get current world state
  - /api/agents - Get agent information
  - /api/climate - Get climate data
  - /api/terrain - Get terrain data
  - /api/resources - Get resource data

## Features

- Dynamic climate system with temperature, precipitation, and wind patterns
- Procedurally generated terrain with elevation, water bodies, and vegetation
- Resource distribution and management
- Agent-based simulation with individual behaviors
- Agents possess open-ended free will, forming cultures and societies
- Real-time visualization and control interface
- Detailed logging and progress tracking
- Natural disaster system simulating earthquakes, hurricanes, and more
- Seasons progress throughout the year, influencing weather and climate
- Realistic day/night cycle with real-world latitude and longitude
- Environments track coordinates for localized time of day
- Two initial agents spawn near Passaic, NJ with no predefined names
- Basic physics system applying Newtonian motion to agents
- Farming fields influenced by soil quality and nutrients
- Natural plant and animal populations spawn in their native habitats
- Simple building system for constructing structures over time
- Fire-making technology enabling cooking and warmth
- Environment state reports current world time for synchronization
- God-view dashboard at `/godview` displays Redis-backed world data



## Development

### Project Structure
```
simulation/
├── engine.py          # Main simulation engine
├── world.py           # World state management
├── climate.py         # Climate system
├── terrain.py         # Terrain generation
├── resources.py       # Resource management
├── agents.py          # Agent system
├── server.py          # Backend server
├── routes.py          # API routes
├── templates/         # Frontend templates
└── static/           # Static assets
```

### Adding New Features
1. Create new module in simulation/
2. Update engine.py to integrate new system
3. Add appropriate routes in routes.py
4. Update frontend to display new data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details
