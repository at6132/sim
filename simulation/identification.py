from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class IdentificationSystem:
    """Represents an agent's identification system and how they identify others."""
    agent_id: str
    identifiers: Dict[str, str] = field(default_factory=dict)  # Maps agent_id to their identifier
    identifier_types: Dict[str, str] = field(default_factory=dict)  # Maps agent_id to type of identifier used
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

    # Types of identifiers that can emerge
    IDENTIFIER_TYPES = {
        "physical": "Based on physical characteristics",
        "behavioral": "Based on behavior patterns",
        "location": "Based on where they live",
        "role": "Based on their role in society",
        "sound": "Based on sounds they make",
        "gesture": "Based on gestures they use",
        "abstract": "Based on abstract concepts"
    }

    def add_identifier(self, target_id: str, identifier: str, identifier_type: str) -> None:
        """Add or update an identifier for another agent."""
        self.identifiers[target_id] = identifier
        self.identifier_types[target_id] = identifier_type
        self.last_update = time.time()

    def get_identifier(self, target_id: str) -> Optional[str]:
        """Get the identifier for another agent."""
        return self.identifiers.get(target_id)

    def get_identifier_type(self, target_id: str) -> Optional[str]:
        """Get the type of identifier used for another agent."""
        return self.identifier_types.get(target_id)

    def generate_identifier(self, target_agent: 'Agent', identifier_type: str) -> str:
        """Generate a new identifier for another agent based on the specified type."""
        if identifier_type == "physical":
            # Use physical characteristics
            traits = []
            if target_agent.genes.strength > 0.7:
                traits.append("strong")
            if target_agent.genes.adaptability > 0.7:
                traits.append("adaptable")
            if target_agent.health > 0.8:
                traits.append("healthy")
            return " ".join(traits) if traits else "person"

        elif identifier_type == "behavioral":
            # Use behavioral patterns
            behaviors = []
            if target_agent.genes.social_drive > 0.7:
                behaviors.append("social")
            if target_agent.genes.creativity > 0.7:
                behaviors.append("creative")
            if target_agent.genes.curiosity > 0.7:
                behaviors.append("curious")
            return " ".join(behaviors) if behaviors else "person"

        elif identifier_type == "location":
            # Use location-based identifiers
            terrain = target_agent.world.get_terrain_at(target_agent.longitude, target_agent.latitude)
            return f"{terrain.type.value} dweller"

        elif identifier_type == "role":
            # Use role-based identifiers
            if target_agent.tribe_id:
                return "tribe member"
            elif target_agent.settlement_id:
                return "settlement dweller"
            else:
                return "wanderer"

        elif identifier_type == "sound":
            # Use sound-based identifiers
            sounds = ["click", "whistle", "hum", "chirp", "buzz"]
            return random.choice(sounds)

        elif identifier_type == "gesture":
            # Use gesture-based identifiers
            gestures = ["wave", "nod", "point", "bow", "dance"]
            return random.choice(gestures)

        elif identifier_type == "abstract":
            # Use abstract concept-based identifiers
            concepts = ["light", "dark", "fast", "slow", "high", "low"]
            return random.choice(concepts)

        return "person"  # Default identifier

    def update_identifiers(self, world_state: Dict) -> None:
        """Update identifiers based on new information and interactions."""
        nearby_agents = world_state.get("agents", {})
        
        for agent_id, agent in nearby_agents.items():
            if agent_id != self.agent_id:  # Don't identify self
                # Check if we need to update the identifier
                if agent_id not in self.identifiers or random.random() < 0.1:  # 10% chance to update
                    # Choose identifier type based on what we know about the agent
                    identifier_type = random.choice(list(self.IDENTIFIER_TYPES.keys()))
                    new_identifier = self.generate_identifier(agent, identifier_type)
                    self.add_identifier(agent_id, new_identifier, identifier_type)

    def to_dict(self) -> Dict:
        """Convert identification system to dictionary for saving."""
        return {
            "agent_id": self.agent_id,
            "identifiers": self.identifiers,
            "identifier_types": self.identifier_types,
            "created_at": self.created_at,
            "last_update": self.last_update
        } 