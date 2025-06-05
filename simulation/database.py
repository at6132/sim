import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from .utils.logging_config import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    def __init__(self, db_dir: str = "data"):
        self.db_dir = db_dir
        self.ensure_db_directories()
        
    def ensure_db_directories(self):
        """Create necessary database directories if they don't exist."""
        directories = [
            self.db_dir,
            os.path.join(self.db_dir, "agents"),
            os.path.join(self.db_dir, "animals"),
            os.path.join(self.db_dir, "marine"),
            os.path.join(self.db_dir, "world"),
            os.path.join(self.db_dir, "events"),
            os.path.join(self.db_dir, "civilization")
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
    
    def save_agent(self, agent_id: str, data: Dict[str, Any]):
        """Save agent data to JSON file."""
        file_path = os.path.join(self.db_dir, "agents", f"{agent_id}.json")
        self._save_json(file_path, data)
    
    def load_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent data from JSON file."""
        file_path = os.path.join(self.db_dir, "agents", f"{agent_id}.json")
        return self._load_json(file_path)
    
    def save_animal(self, animal_id: str, data: Dict[str, Any]):
        """Save animal data to JSON file."""
        file_path = os.path.join(self.db_dir, "animals", f"{animal_id}.json")
        self._save_json(file_path, data)
    
    def load_animal(self, animal_id: str) -> Optional[Dict[str, Any]]:
        """Load animal data from JSON file."""
        file_path = os.path.join(self.db_dir, "animals", f"{animal_id}.json")
        return self._load_json(file_path)
    
    def save_marine_creature(self, creature_id: str, data: Dict[str, Any]):
        """Save marine creature data to JSON file."""
        file_path = os.path.join(self.db_dir, "marine", f"{creature_id}.json")
        self._save_json(file_path, data)
    
    def load_marine_creature(self, creature_id: str) -> Optional[Dict[str, Any]]:
        """Load marine creature data from JSON file."""
        file_path = os.path.join(self.db_dir, "marine", f"{creature_id}.json")
        return self._load_json(file_path)
    
    def save_world_state(self, data: Dict[str, Any]):
        """Save world state to JSON file."""
        file_path = os.path.join(self.db_dir, "world", "state.json")
        self._save_json(file_path, data)
    
    def load_world_state(self) -> Optional[Dict[str, Any]]:
        """Load world state from JSON file."""
        file_path = os.path.join(self.db_dir, "world", "state.json")
        return self._load_json(file_path)
    
    def save_event(self, event: Dict[str, Any]):
        """Save event to JSON file with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.db_dir, "events", f"event_{timestamp}.json")
        self._save_json(file_path, event)
    
    def save_civilization_data(self, data: Dict[str, Any]):
        """Save civilization data (inventions, religions, languages) to JSON file."""
        file_path = os.path.join(self.db_dir, "civilization", "data.json")
        self._save_json(file_path, data)
    
    def load_civilization_data(self) -> Optional[Dict[str, Any]]:
        """Load civilization data from JSON file."""
        file_path = os.path.join(self.db_dir, "civilization", "data.json")
        return self._load_json(file_path)
    
    def _save_json(self, file_path: str, data: Dict[str, Any]):
        """Save data to JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved data to {file_path}")
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {str(e)}")
    
    def _load_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load data from JSON file."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            return None
    
    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent data."""
        agents = {}
        agent_dir = os.path.join(self.db_dir, "agents")
        for filename in os.listdir(agent_dir):
            if filename.endswith('.json'):
                agent_id = filename[:-5]  # Remove .json extension
                agent_data = self.load_agent(agent_id)
                if agent_data:
                    agents[agent_id] = agent_data
        return agents
    
    def get_all_animals(self) -> Dict[str, Dict[str, Any]]:
        """Get all animal data."""
        animals = {}
        animal_dir = os.path.join(self.db_dir, "animals")
        for filename in os.listdir(animal_dir):
            if filename.endswith('.json'):
                animal_id = filename[:-5]
                animal_data = self.load_animal(animal_id)
                if animal_data:
                    animals[animal_id] = animal_data
        return animals
    
    def get_all_marine_creatures(self) -> Dict[str, Dict[str, Any]]:
        """Get all marine creature data."""
        creatures = {}
        marine_dir = os.path.join(self.db_dir, "marine")
        for filename in os.listdir(marine_dir):
            if filename.endswith('.json'):
                creature_id = filename[:-5]
                creature_data = self.load_marine_creature(creature_id)
                if creature_data:
                    creatures[creature_id] = creature_data
        return creatures
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get most recent events."""
        events = []
        event_dir = os.path.join(self.db_dir, "events")
        event_files = sorted(os.listdir(event_dir), reverse=True)[:limit]
        
        for filename in event_files:
            if filename.endswith('.json'):
                file_path = os.path.join(event_dir, filename)
                event_data = self._load_json(file_path)
                if event_data:
                    events.append(event_data)
        
        return events 