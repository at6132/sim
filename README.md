# 🧠 AI Civilization Simulation

An **ambitious simulation** where intelligent life begins at the most primitive level and evolves completely on its own — driven by curiosity, survival, reproduction, and learning. Agents start like "Adam and Eve" with no knowledge of the world. They must discover fire, find food and water, survive sickness, build shelters, form tribes, and — if they live long enough — develop roads, technology, medicine, cars, and even skyscrapers.

No knowledge is preprogrammed. Every idea must emerge through experience, memory, and limited GPT-4 cognition, guided only by genetics, environmental input, and their desire to understand and adapt.

---

## 🌟 Features

- 🤖 **Autonomous Agents**
  Each agent has a genetic profile, evolving memory, and biological needs and is attached to a context aware LLM seperate for each agent that would have access to its memeory, its age, feelings, enviroment, health, genetics etc... (hunger, thirst, sickness, aging, reproduction, emotion, etc.).

- 🧬 **Fully Simulated Biology & Reproduction**
  Agents are born, age, fall sick, die, and reproduce. Children inherit mutated genes from parents. Lineages and family trees form organically.

- 🌍 **Dynamic Living World**
  A large 2D world with terrain types (grass, forest, desert, water, mountain), climates, day/night cycle, seasons, and resource distribution.

- 🧠 **GPT-4 Driven Cognition**
  Agents "think" in real time using their current state, memories, environment, and biological needs. They can invent tools, rituals, laws, and ideas — *if they think to*.

- 🏛️ **Emergent Civilization**
  - Tribes, languages, social roles, rituals
  - Villages → towns → cities
  - Schools, governments, religions
  - Eventually: electronics, transportation, medicine, skyscrapers, etc.

- 💬 **Emotion & Interaction System**
  Agents feel fear, love, pain, joy, loneliness — driving behavior, attachment, exploration, conflict, and diplomacy.

- 🛠️ **Self-Driven Progression**
  No tech tree. Agents invent things if they imagine it. Fire, wheels, buildings, metals, electricity — they must discover it all from scratch.

- 📈 **Real-Time Time Engine**
  - 1 real-life hour = 2 simulation days
  - Agents age realistically (1 year ≈ 365 sim days)
  - Seasonal shifts, sickness waves, generational turnover

---

## 🖥️ Frontend Interface

Accessible at `http://localhost:5000`

- 🗺️ **Live 2D World Map**  
  - Agents, terrain, tribes, buildings, animals, weather  
  - Click agents to view stats, health, emotions, thoughts, and memory

- 📜 **Agent Panel**  
  - View individual gene profiles, relationships, status, cognition logs

- 🧬 **Family Trees**  
  - Explore genealogical lineage and inheritance over generations

- 🛖 **Civilization Tracker**  
  - Inventions, religion emergence, language mapping  
  - Global timeline of major breakthroughs

- 📊 **Overlay Systems**  
  - Tribe boundaries  
  - Disease spread  
  - Language divergence  
  - Cultural hotspots

---

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/ai-civ-sim.git
cd ai-civ-sim
```

2. Create a virtual environment and activate it:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
OPENAI_API_KEY=your_api_key_here
```

## 🚀 Running the Simulation

1. Start the simulation server:
```bash
python api.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Use the control panel to:
   - Start/Pause the simulation
   - Adjust time scale
   - Reset the world
   - View agent details
   - Track civilization progress

## 📊 Monitoring and Analysis

The simulation provides real-time data through the API endpoints:

- `/api/world/state` - Current world state
- `/api/agents` - All agent data
- `/api/agent/<id>` - Specific agent details
- `/api/animals` - Animal population data
- `/api/civilization` - Civilization progress
- `/api/family-trees` - Genealogical data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
