from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class Ideology:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    core_values: List[str] = field(default_factory=list)
    cultural_significance: float = 0.0  # 0-1 scale
    influence: float = 0.0  # 0-1 scale
    followers: Set[str] = field(default_factory=set)  # Set of agent IDs
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Conflict:
    title: str
    participants: List[str]  # List of agent IDs
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    intensity: float = 0.0  # 0-1 scale
    duration: float = 0.0  # Time in hours
    casualties: int = 0
    resources_lost: Dict[str, float] = field(default_factory=dict)
    resolution: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Diplomacy:
    title: str
    participants: List[str]  # List of agent IDs
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    terms: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0  # Time in hours
    success_rate: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class CulturalGroup:
    name: str
    leader: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    members: Set[str] = field(default_factory=set)  # Set of agent IDs
    territory: List[Tuple[float, float]] = field(default_factory=list)
    ideology: Optional[str] = None  # Ideology name
    resources: Dict[str, float] = field(default_factory=dict)
    military_strength: float = 0.0  # 0-1 scale
    cultural_influence: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class CultureSystem:
    def __init__(self, world):
        """Initialize the culture system."""
        self.world = world
        self.ideologies: Dict[str, Ideology] = {}
        self.conflicts: Dict[str, Conflict] = {}
        self.diplomacy: Dict[str, Diplomacy] = {}
        self.groups: Dict[str, CulturalGroup] = {}
        
    def create_ideology(self, name: str, creator: str,
                       description: str = "") -> Ideology:
        """Create a new ideology."""
        if name in self.ideologies:
            logger.warning(f"Ideology {name} already exists")
            return self.ideologies[name]
            
        ideology = Ideology(
            name=name,
            creator=creator,
            description=description
        )
        
        self.ideologies[name] = ideology
        logger.info(f"Created new ideology: {name}")
        return ideology
        
    def create_conflict(self, title: str,
                       participants: List[str], description: str = "") -> Conflict:
        """Create a new conflict."""
        if title in self.conflicts:
            logger.warning(f"Conflict {title} already exists")
            return self.conflicts[title]
            
        conflict = Conflict(
            title=title,
            participants=participants,
            description=description
        )
        
        self.conflicts[title] = conflict
        logger.info(f"Created new conflict: {title}")
        return conflict
        
    def create_diplomacy(self, title: str,
                        participants: List[str], description: str = "") -> Diplomacy:
        """Create a new diplomatic agreement."""
        if title in self.diplomacy:
            logger.warning(f"Diplomacy {title} already exists")
            return self.diplomacy[title]
            
        diplomacy = Diplomacy(
            title=title,
            participants=participants,
            description=description
        )
        
        self.diplomacy[title] = diplomacy
        logger.info(f"Created new diplomacy: {title}")
        return diplomacy
        
    def create_group(self, name: str, leader: str,
                    description: str = "") -> CulturalGroup:
        """Create a new cultural group."""
        if name in self.groups:
            logger.warning(f"Group {name} already exists")
            return self.groups[name]
            
        group = CulturalGroup(
            name=name,
            leader=leader,
            description=description
        )
        
        self.groups[name] = group
        logger.info(f"Created new group: {name}")
        return group
        
    def add_follower(self, ideology: str, agent_id: str):
        """Add a follower to an ideology."""
        if ideology in self.ideologies:
            self.ideologies[ideology].followers.add(agent_id)
            logger.info(f"Added follower {agent_id} to ideology {ideology}")
            
    def remove_follower(self, ideology: str, agent_id: str):
        """Remove a follower from an ideology."""
        if ideology in self.ideologies:
            self.ideologies[ideology].followers.discard(agent_id)
            logger.info(f"Removed follower {agent_id} from ideology {ideology}")
            
    def add_group_member(self, group: str, agent_id: str):
        """Add a member to a cultural group."""
        if group in self.groups:
            self.groups[group].members.add(agent_id)
            logger.info(f"Added member {agent_id} to group {group}")
            
    def remove_group_member(self, group: str, agent_id: str):
        """Remove a member from a cultural group."""
        if group in self.groups:
            self.groups[group].members.discard(agent_id)
            logger.info(f"Removed member {agent_id} from group {group}")
            
    def evolve_ideology(self, name: str, time_delta: float):
        """Evolve an ideology over time."""
        if name not in self.ideologies:
            return
            
        ideology = self.ideologies[name]
        
        # Update influence based on number of followers
        follower_factor = min(1.0, len(ideology.followers) / 100.0)
        ideology.influence = (ideology.influence * 0.9 + follower_factor * 0.1)
        
        # Update cultural significance
        if len(ideology.followers) > 0:
            ideology.cultural_significance = min(1.0,
                ideology.cultural_significance + 0.01 * time_delta)
                
    def evolve_conflict(self, title: str, time_delta: float):
        """Evolve a conflict over time."""
        if title not in self.conflicts:
            return
            
        conflict = self.conflicts[title]
        
        # Update duration
        conflict.duration += time_delta
        
        # Update intensity
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            conflict.intensity = min(1.0,
                conflict.intensity + random.uniform(0.1, 0.2))
                
        # Check for resolution
        if conflict.intensity > 0.8 and random.random() < 0.05 * time_delta:
            self._resolve_conflict(conflict)
            
    def _resolve_conflict(self, conflict: Conflict):
        """Resolve a conflict."""
        # Determine resolution type
        resolution_types = [
            "Peace treaty",
            "Territorial division",
            "Resource sharing",
            "Cultural exchange",
            "Military victory"
        ]
        
        conflict.resolution = random.choice(resolution_types)
        logger.info(f"Conflict {conflict.title} resolved with {conflict.resolution}")
        
    def evolve_diplomacy(self, title: str, time_delta: float):
        """Evolve a diplomatic agreement over time."""
        if title not in self.diplomacy:
            return
            
        diplomacy = self.diplomacy[title]
        
        # Update duration
        diplomacy.duration += time_delta
        
        # Update success rate
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            diplomacy.success_rate = min(1.0,
                diplomacy.success_rate + random.uniform(0.05, 0.1))
                
    def evolve_group(self, name: str, time_delta: float):
        """Evolve a cultural group over time."""
        if name not in self.groups:
            return
            
        group = self.groups[name]
        
        # Update cultural influence
        member_factor = min(1.0, len(group.members) / 100.0)
        group.cultural_influence = (group.cultural_influence * 0.9 + member_factor * 0.1)
        
        # Update military strength
        if random.random() < 0.05 * time_delta:  # 5% chance per hour
            group.military_strength = min(1.0,
                group.military_strength + random.uniform(0.01, 0.05))
                
    def update(self, time_delta: float):
        """Update culture system state."""
        # Evolve ideologies
        for name in list(self.ideologies.keys()):
            self.evolve_ideology(name, time_delta)
            
        # Evolve conflicts
        for title in list(self.conflicts.keys()):
            self.evolve_conflict(title, time_delta)
            
        # Evolve diplomacy
        for title in list(self.diplomacy.keys()):
            self.evolve_diplomacy(title, time_delta)
            
        # Evolve groups
        for name in list(self.groups.keys()):
            self.evolve_group(name, time_delta)
            
    def to_dict(self) -> Dict:
        """Convert culture system state to dictionary for serialization."""
        return {
            "ideologies": {
                name: {
                    "name": ideology.name,
                    "creator": ideology.creator,
                    "creation_date": ideology.creation_date,
                    "description": ideology.description,
                    "core_values": ideology.core_values,
                    "cultural_significance": ideology.cultural_significance,
                    "influence": ideology.influence,
                    "followers": list(ideology.followers),
                    "created_at": ideology.created_at,
                    "last_update": ideology.last_update
                }
                for name, ideology in self.ideologies.items()
            },
            "conflicts": {
                title: {
                    "title": conflict.title,
                    "participants": conflict.participants,
                    "creation_date": conflict.creation_date,
                    "description": conflict.description,
                    "intensity": conflict.intensity,
                    "duration": conflict.duration,
                    "casualties": conflict.casualties,
                    "resources_lost": conflict.resources_lost,
                    "resolution": conflict.resolution,
                    "created_at": conflict.created_at,
                    "last_update": conflict.last_update
                }
                for title, conflict in self.conflicts.items()
            },
            "diplomacy": {
                title: {
                    "title": diplomacy.title,
                    "participants": diplomacy.participants,
                    "creation_date": diplomacy.creation_date,
                    "description": diplomacy.description,
                    "terms": diplomacy.terms,
                    "duration": diplomacy.duration,
                    "success_rate": diplomacy.success_rate,
                    "created_at": diplomacy.created_at,
                    "last_update": diplomacy.last_update
                }
                for title, diplomacy in self.diplomacy.items()
            },
            "groups": {
                name: {
                    "name": group.name,
                    "leader": group.leader,
                    "creation_date": group.creation_date,
                    "description": group.description,
                    "members": list(group.members),
                    "territory": group.territory,
                    "ideology": group.ideology,
                    "resources": group.resources,
                    "military_strength": group.military_strength,
                    "cultural_influence": group.cultural_influence,
                    "created_at": group.created_at,
                    "last_update": group.last_update
                }
                for name, group in self.groups.items()
            }
        } 