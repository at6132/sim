from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum
import random
from datetime import datetime
import time

class RelationshipType(Enum):
    FRIEND = "friend"
    FAMILY = "family"
    ROMANTIC = "romantic"
    RIVAL = "rival"
    ENEMY = "enemy"
    MENTOR = "mentor"
    STUDENT = "student"
    ALLY = "ally"
    NEUTRAL = "neutral"

@dataclass
class Relationship:
    type: RelationshipType
    target_id: str
    strength: float  # -1.0 to 1.0
    trust: float  # 0.0 to 1.0
    history: List[Dict] = field(default_factory=list)
    last_interaction: float = field(default_factory=lambda: time.time())
    shared_experiences: Set[str] = field(default_factory=set)
    conflicts: List[Dict] = field(default_factory=list)

class Relationships:
    def __init__(self):
        self.relationships: Dict[str, Relationship] = {}  # target_id -> relationship
        self.social_network: Dict[str, Set[str]] = {}  # agent_id -> set of connected agent_ids
        self.last_update = time.time()
        
    def update(self, time_delta: float) -> None:
        """Update relationships over time."""
        current_time = time.time()
        
        # Update relationship strengths based on time
        for relationship in self.relationships.values():
            time_since_interaction = current_time - relationship.last_interaction
            
            # Relationships decay over time without interaction
            if time_since_interaction > 24 * 3600:  # 24 hours
                decay_factor = min(1.0, time_since_interaction / (7 * 24 * 3600))  # Decay over a week
                if relationship.type in [RelationshipType.FRIEND, RelationshipType.FAMILY, RelationshipType.ROMANTIC]:
                    relationship.strength = max(-1.0, relationship.strength - 0.1 * decay_factor * time_delta)
                elif relationship.type in [RelationshipType.RIVAL, RelationshipType.ENEMY]:
                    relationship.strength = min(1.0, relationship.strength + 0.05 * decay_factor * time_delta)
                    
            # Trust increases with positive interactions
            positive_interactions = sum(1 for event in relationship.history[-10:] 
                                     if event.get("impact", 0) > 0)
            if positive_interactions > 0:
                relationship.trust = min(1.0, relationship.trust + 0.01 * positive_interactions * time_delta)
                
    def add_relationship(self, target_id: str, relationship_type: RelationshipType) -> None:
        """Add a new relationship."""
        if target_id not in self.relationships:
            self.relationships[target_id] = Relationship(
                type=relationship_type,
                target_id=target_id,
                strength=0.0,
                trust=0.5
            )
            if target_id not in self.social_network:
                self.social_network[target_id] = set()
                
    def update_relationship(self, target_id: str, event: Dict) -> None:
        """Update a relationship based on an event."""
        if target_id in self.relationships:
            relationship = self.relationships[target_id]
            relationship.history.append(event)
            relationship.last_interaction = time.time()
            
            # Update strength based on event impact
            impact = event.get("impact", 0)
            relationship.strength = max(-1.0, min(1.0, relationship.strength + impact))
            
            # Update trust based on event type
            if event.get("type") == "betrayal":
                relationship.trust = max(0.0, relationship.trust - 0.3)
            elif event.get("type") == "support":
                relationship.trust = min(1.0, relationship.trust + 0.1)
                
            # Add to shared experiences if significant
            if abs(impact) > 0.3:
                relationship.shared_experiences.add(event.get("description", ""))
                
    def add_conflict(self, target_id: str, conflict: Dict) -> None:
        """Add a conflict to a relationship."""
        if target_id in self.relationships:
            self.relationships[target_id].conflicts.append(conflict)
            
    def get_relationship_strength(self, target_id: str) -> float:
        """Get the current strength of a relationship."""
        return self.relationships.get(target_id, Relationship(
            type=RelationshipType.NEUTRAL,
            target_id=target_id,
            strength=0.0,
            trust=0.5
        )).strength
        
    def get_relationship_trust(self, target_id: str) -> float:
        """Get the current trust level of a relationship."""
        return self.relationships.get(target_id, Relationship(
            type=RelationshipType.NEUTRAL,
            target_id=target_id,
            strength=0.0,
            trust=0.5
        )).trust
        
    def to_dict(self) -> Dict:
        """Convert relationships state to dictionary for serialization."""
        return {
            "relationships": {
                target_id: {
                    "type": rel.type.value,
                    "strength": rel.strength,
                    "trust": rel.trust,
                    "history": rel.history,
                    "last_interaction": rel.last_interaction,
                    "shared_experiences": list(rel.shared_experiences),
                    "conflicts": rel.conflicts
                }
                for target_id, rel in self.relationships.items()
            },
            "social_network": {
                agent_id: list(connections)
                for agent_id, connections in self.social_network.items()
            }
        } 