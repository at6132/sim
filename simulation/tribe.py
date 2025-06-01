from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import random
import logging

logger = logging.getLogger(__name__)

class TribeType(Enum):
    NOMADIC = "nomadic"
    HUNTER_GATHERER = "hunter_gatherer"
    AGRICULTURAL = "agricultural"
    PASTORAL = "pastoral"
    TRADING = "trading"
    WARRIOR = "warrior"

class TribeStatus(Enum):
    PEACEFUL = "peaceful"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    EXPANSIONIST = "expansionist"
    ISOLATIONIST = "isolationist"

@dataclass
class TribeTerritory:
    """Represents a territory claimed by a tribe"""
    center_longitude: float
    center_latitude: float
    radius: float  # in kilometers
    claimed_by: Optional[str] = None
    resources: Dict[str, float] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)

@dataclass
class Tribe:
    """Represents a tribe in the simulation"""
    id: str
    name: str
    leader_id: str
    members: List[str]
    territory: Optional[TribeTerritory]
    culture: Dict[str, float]
    history: List[Dict]
    resources: Dict[str, float]
    relationships: Dict[str, float]  # tribe_id -> relationship value

    def __init__(self, id: str, name: str, leader_id: str, longitude: float, latitude: float, radius: float = 10.0):
        self.id = id
        self.name = name
        self.leader_id = leader_id
        self.members = [leader_id]
        self.territory = TribeTerritory(
            center_longitude=longitude,
            center_latitude=latitude,
            radius=radius,
            claimed_by=id
        )
        self.culture = {
            'aggression': 0.5,
            'cooperation': 0.5,
            'innovation': 0.5,
            'tradition': 0.5
        }
        self.history = []
        self.resources = {}
        self.relationships = {}

    def is_in_territory(self, longitude: float, latitude: float) -> bool:
        """Check if a location is within the tribe's territory"""
        if not self.territory:
            return False
        distance = self.world.get_distance(
            longitude, latitude,
            self.territory.center_longitude,
            self.territory.center_latitude
        )
        return distance <= self.territory.radius

    def expand_territory(self, new_longitude: float, new_latitude: float, new_radius: float) -> None:
        """Expand the tribe's territory to include a new area"""
        if not self.territory:
            self.territory = TribeTerritory(
                center_longitude=new_longitude,
                center_latitude=new_latitude,
                radius=new_radius,
                claimed_by=self.id
            )
        else:
            # Calculate new center as midpoint between old center and new location
            self.territory.center_longitude = (self.territory.center_longitude + new_longitude) / 2
            self.territory.center_latitude = (self.territory.center_latitude + new_latitude) / 2
            self.territory.radius = max(self.territory.radius, new_radius)

class TribeSystem:
    def __init__(self):
        self.tribes: Dict[str, Dict] = {}
        self.territories: Dict[str, TribeTerritory] = {}
        self.relationships: Dict[str, Dict[str, TribeRelationship]] = {}
        self.tribe_types = list(TribeType)
        self.tribe_statuses = list(TribeStatus)
        
    def create_tribe(self, 
                    name: str,
                    position: Tuple[int, int],
                    tribe_type: Optional[TribeType] = None,
                    initial_members: Optional[List[str]] = None) -> str:
        """Create a new tribe."""
        tribe_id = f"tribe_{len(self.tribes)}"
        
        if tribe_type is None:
            tribe_type = random.choice(self.tribe_types)
            
        tribe = {
            "id": tribe_id,
            "name": name,
            "type": tribe_type,
            "status": random.choice(self.tribe_statuses),
            "members": set(initial_members or []),
            "resources": {},
            "knowledge": set(),
            "traditions": set(),
            "beliefs": set(),
            "created_at": 0.0  # Will be set by world time
        }
        
        # Create territory
        territory = TribeTerritory(
            center_longitude=position[0],
            center_latitude=position[1],
            radius=10.0,  # Initial territory size
            resources={},
            claimed_by=tribe_id
        )
        
        self.tribes[tribe_id] = tribe
        self.territories[tribe_id] = territory
        self.relationships[tribe_id] = {}
        
        logger.info(f"Created new tribe: {name} ({tribe_type.value})")
        return tribe_id
        
    def add_member(self, tribe_id: str, agent_id: str) -> bool:
        """Add a member to a tribe."""
        if tribe_id not in self.tribes:
            return False
            
        self.tribes[tribe_id]["members"].add(agent_id)
        return True
        
    def remove_member(self, tribe_id: str, agent_id: str) -> bool:
        """Remove a member from a tribe."""
        if tribe_id not in self.tribes:
            return False
            
        self.tribes[tribe_id]["members"].discard(agent_id)
        return True
        
    def update_territory(self, tribe_id: str, new_center: Tuple[int, int], new_radius: int) -> bool:
        """Update a tribe's territory."""
        if tribe_id not in self.tribes:
            return False
            
        self.territories[tribe_id].center_longitude = new_center[0]
        self.territories[tribe_id].center_latitude = new_center[1]
        self.territories[tribe_id].radius = new_radius
        return True
        
    def get_tribe_at_position(self, longitude: float, latitude: float) -> Optional[str]:
        """Get the tribe ID at the given position"""
        for tribe_id, tribe in self.tribes.items():
            if tribe.territory:
                distance = self.world.get_distance(
                    longitude, latitude,
                    tribe.territory.center_longitude,
                    tribe.territory.center_latitude
                )
                if distance <= tribe.territory.radius:
                    return tribe_id
        return None
        
    def update_relationship(self, 
                          tribe1_id: str, 
                          tribe2_id: str, 
                          interaction_type: str,
                          strength_change: float) -> None:
        """Update the relationship between two tribes."""
        if tribe1_id not in self.relationships:
            self.relationships[tribe1_id] = {}
        if tribe2_id not in self.relationships:
            self.relationships[tribe2_id] = {}
            
        # Update relationship in both directions
        for t1, t2 in [(tribe1_id, tribe2_id), (tribe2_id, tribe1_id)]:
            if t2 not in self.relationships[t1]:
                self.relationships[t1][t2] = TribeRelationship(
                    tribe_id=t2,
                    status="neutral",
                    strength=0.5,
                    history=[],
                    last_interaction=0.0
                )
                
            rel = self.relationships[t1][t2]
            rel.strength = max(0.0, min(1.0, rel.strength + strength_change))
            
            # Update status based on strength
            if rel.strength > 0.7:
                rel.status = "allied"
            elif rel.strength < 0.3:
                rel.status = "hostile"
            else:
                rel.status = "neutral"
                
            rel.history.append({
                "type": interaction_type,
                "strength_change": strength_change,
                "time": 0.0  # Will be set by world time
            })
            
    def get_tribe_resources(self, tribe_id: str) -> Dict[str, float]:
        """Get a tribe's resources."""
        return self.tribes.get(tribe_id, {}).get("resources", {})
        
    def add_tribe_resource(self, tribe_id: str, resource_type: str, amount: float) -> bool:
        """Add resources to a tribe."""
        if tribe_id not in self.tribes:
            return False
            
        if "resources" not in self.tribes[tribe_id]:
            self.tribes[tribe_id]["resources"] = {}
            
        current = self.tribes[tribe_id]["resources"].get(resource_type, 0.0)
        self.tribes[tribe_id]["resources"][resource_type] = current + amount
        return True
        
    def consume_tribe_resource(self, tribe_id: str, resource_type: str, amount: float) -> bool:
        """Consume resources from a tribe."""
        if tribe_id not in self.tribes:
            return False
            
        current = self.tribes[tribe_id]["resources"].get(resource_type, 0.0)
        if current < amount:
            return False
            
        self.tribes[tribe_id]["resources"][resource_type] = current - amount
        return True
        
    def add_tribe_knowledge(self, tribe_id: str, knowledge: str) -> bool:
        """Add knowledge to a tribe."""
        if tribe_id not in self.tribes:
            return False
            
        self.tribes[tribe_id]["knowledge"].add(knowledge)
        return True
        
    def add_tribe_tradition(self, tribe_id: str, tradition: str) -> bool:
        """Add a tradition to a tribe."""
        if tribe_id not in self.tribes:
            return False
            
        self.tribes[tribe_id]["traditions"].add(tradition)
        return True
        
    def add_tribe_belief(self, tribe_id: str, belief: str) -> bool:
        """Add a belief to a tribe."""
        if tribe_id not in self.tribes:
            return False
            
        self.tribes[tribe_id]["beliefs"].add(belief)
        return True
        
    def get_tribe_stats(self, tribe_id: str) -> Dict:
        """Get statistics about a tribe."""
        if tribe_id not in self.tribes:
            return {}
            
        tribe = self.tribes[tribe_id]
        return {
            "name": tribe["name"],
            "type": tribe["type"].value,
            "status": tribe["status"].value,
            "member_count": len(tribe["members"]),
            "resource_count": len(tribe["resources"]),
            "knowledge_count": len(tribe["knowledge"]),
            "tradition_count": len(tribe["traditions"]),
            "belief_count": len(tribe["beliefs"]),
            "territory_size": self.territories[tribe_id].radius * self.territories[tribe_id].radius * 3.14159
        }
        
    def to_dict(self) -> Dict:
        """Convert tribe system state to dictionary for serialization."""
        return {
            "tribes": {
                tribe_id: {
                    "name": tribe["name"],
                    "type": tribe["type"].value,
                    "status": tribe["status"].value,
                    "members": list(tribe["members"]),
                    "resources": tribe["resources"],
                    "knowledge": list(tribe["knowledge"]),
                    "traditions": list(tribe["traditions"]),
                    "beliefs": list(tribe["beliefs"]),
                    "created_at": tribe["created_at"]
                }
                for tribe_id, tribe in self.tribes.items()
            },
            "territories": {
                tribe_id: {
                    "center_longitude": tribe.center_longitude,
                    "center_latitude": tribe.center_latitude,
                    "radius": tribe.radius,
                    "claimed_by": tribe.claimed_by,
                    "resources": tribe.resources,
                    "history": tribe.history
                }
                for tribe_id, tribe in self.territories.items()
            },
            "relationships": {
                tribe_id: {
                    other_id: {
                        "status": rel.status,
                        "strength": rel.strength,
                        "history": rel.history,
                        "last_interaction": rel.last_interaction
                    }
                    for other_id, rel in relationships.items()
                }
                for tribe_id, relationships in self.relationships.items()
            }
        } 