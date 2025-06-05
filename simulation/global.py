from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class Treaty:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    signatories: List[str] = field(default_factory=list)  # List of agent IDs
    terms: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0  # Time in hours
    success_rate: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Religion:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    beliefs: List[str] = field(default_factory=list)
    practices: List[str] = field(default_factory=list)
    followers: Set[str] = field(default_factory=set)  # Set of agent IDs
    influence: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class War:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    participants: List[str] = field(default_factory=list)  # List of agent IDs
    alliances: Dict[str, List[str]] = field(default_factory=dict)
    casualties: int = 0
    resources_lost: Dict[str, float] = field(default_factory=dict)
    intensity: float = 0.0  # 0-1 scale
    duration: float = 0.0  # Time in hours
    resolution: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class GlobalInstitution:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    purpose: str = ""
    members: List[str] = field(default_factory=list)  # List of agent IDs
    influence: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class GlobalSystem:
    def __init__(self, world):
        """Initialize the global system."""
        self.world = world
        self.treaties: Dict[str, Treaty] = {}
        self.religions: Dict[str, Religion] = {}
        self.wars: Dict[str, War] = {}
        self.institutions: Dict[str, GlobalInstitution] = {}
        
    def create_treaty(self, name: str, creator: str,
                     description: str = "") -> Treaty:
        """Create a new treaty."""
        if name in self.treaties:
            logger.warning(f"Treaty {name} already exists")
            return self.treaties[name]
            
        treaty = Treaty(
            name=name,
            creator=creator,
            description=description
        )
        
        self.treaties[name] = treaty
        logger.info(f"Created new treaty: {name}")
        return treaty
        
    def create_religion(self, name: str, creator: str,
                       description: str = "") -> Religion:
        """Create a new religion."""
        if name in self.religions:
            logger.warning(f"Religion {name} already exists")
            return self.religions[name]
            
        religion = Religion(
            name=name,
            creator=creator,
            description=description
        )
        
        self.religions[name] = religion
        logger.info(f"Created new religion: {name}")
        return religion
        
    def create_war(self, name: str, creator: str,
                  description: str = "") -> War:
        """Create a new war."""
        if name in self.wars:
            logger.warning(f"War {name} already exists")
            return self.wars[name]
            
        war = War(
            name=name,
            creator=creator,
            description=description
        )
        
        self.wars[name] = war
        logger.info(f"Created new war: {name}")
        return war
        
    def create_institution(self, name: str, creator: str,
                         description: str = "", purpose: str = "") -> GlobalInstitution:
        """Create a new global institution."""
        if name in self.institutions:
            logger.warning(f"Institution {name} already exists")
            return self.institutions[name]
            
        institution = GlobalInstitution(
            name=name,
            creator=creator,
            description=description,
            purpose=purpose
        )
        
        self.institutions[name] = institution
        logger.info(f"Created new institution: {name}")
        return institution
        
    def add_treaty_signatory(self, treaty: str, agent_id: str):
        """Add a signatory to a treaty."""
        if treaty in self.treaties:
            self.treaties[treaty].signatories.append(agent_id)
            logger.info(f"Added signatory {agent_id} to treaty {treaty}")
            
    def add_religion_follower(self, religion: str, agent_id: str):
        """Add a follower to a religion."""
        if religion in self.religions:
            self.religions[religion].followers.add(agent_id)
            logger.info(f"Added follower {agent_id} to religion {religion}")
            
    def remove_religion_follower(self, religion: str, agent_id: str):
        """Remove a follower from a religion."""
        if religion in self.religions:
            self.religions[religion].followers.discard(agent_id)
            logger.info(f"Removed follower {agent_id} from religion {religion}")
            
    def add_war_participant(self, war: str, agent_id: str):
        """Add a participant to a war."""
        if war in self.wars:
            self.wars[war].participants.append(agent_id)
            logger.info(f"Added participant {agent_id} to war {war}")
            
    def add_institution_member(self, institution: str, agent_id: str):
        """Add a member to a global institution."""
        if institution in self.institutions:
            self.institutions[institution].members.append(agent_id)
            logger.info(f"Added member {agent_id} to institution {institution}")
            
    def evolve_treaty(self, name: str, time_delta: float):
        """Evolve a treaty over time."""
        if name not in self.treaties:
            return
            
        treaty = self.treaties[name]
        
        # Update duration
        treaty.duration += time_delta
        
        # Update success rate based on signatories
        signatory_factor = min(1.0, len(treaty.signatories) / 100.0)
        treaty.success_rate = (treaty.success_rate * 0.9 + signatory_factor * 0.1)
        
    def evolve_religion(self, name: str, time_delta: float):
        """Evolve a religion over time."""
        if name not in self.religions:
            return
            
        religion = self.religions[name]
        
        # Update influence based on followers
        follower_factor = min(1.0, len(religion.followers) / 1000.0)
        religion.influence = (religion.influence * 0.9 + follower_factor * 0.1)
        
    def evolve_war(self, name: str, time_delta: float):
        """Evolve a war over time."""
        if name not in self.wars:
            return
            
        war = self.wars[name]
        
        # Update duration
        war.duration += time_delta
        
        # Update intensity
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            war.intensity = min(1.0,
                war.intensity + random.uniform(0.1, 0.2))
                
        # Check for resolution
        if war.intensity > 0.8 and random.random() < 0.05 * time_delta:
            self._resolve_war(war)
            
    def _resolve_war(self, war: War):
        """Resolve a war."""
        # Determine resolution type
        resolution_types = [
            "Peace treaty",
            "Territorial division",
            "Resource sharing",
            "Cultural exchange",
            "Military victory"
        ]
        
        war.resolution = random.choice(resolution_types)
        logger.info(f"War {war.name} resolved with {war.resolution}")
        
    def evolve_institution(self, name: str, time_delta: float):
        """Evolve a global institution over time."""
        if name not in self.institutions:
            return
            
        institution = self.institutions[name]
        
        # Update influence based on members
        member_factor = min(1.0, len(institution.members) / 100.0)
        institution.influence = (institution.influence * 0.9 + member_factor * 0.1)
        
    def update(self, time_delta: float):
        """Update global system state."""
        # Evolve treaties
        for name in list(self.treaties.keys()):
            self.evolve_treaty(name, time_delta)
            
        # Evolve religions
        for name in list(self.religions.keys()):
            self.evolve_religion(name, time_delta)
            
        # Evolve wars
        for name in list(self.wars.keys()):
            self.evolve_war(name, time_delta)
            
        # Evolve institutions
        for name in list(self.institutions.keys()):
            self.evolve_institution(name, time_delta)
            
    def to_dict(self) -> Dict:
        """Convert global system state to dictionary for serialization."""
        return {
            "treaties": {
                name: {
                    "name": treaty.name,
                    "creator": treaty.creator,
                    "creation_date": treaty.creation_date,
                    "description": treaty.description,
                    "signatories": treaty.signatories,
                    "terms": treaty.terms,
                    "duration": treaty.duration,
                    "success_rate": treaty.success_rate,
                    "created_at": treaty.created_at,
                    "last_update": treaty.last_update
                }
                for name, treaty in self.treaties.items()
            },
            "religions": {
                name: {
                    "name": religion.name,
                    "creator": religion.creator,
                    "creation_date": religion.creation_date,
                    "description": religion.description,
                    "beliefs": religion.beliefs,
                    "practices": religion.practices,
                    "followers": list(religion.followers),
                    "influence": religion.influence,
                    "created_at": religion.created_at,
                    "last_update": religion.last_update
                }
                for name, religion in self.religions.items()
            },
            "wars": {
                name: {
                    "name": war.name,
                    "creator": war.creator,
                    "creation_date": war.creation_date,
                    "description": war.description,
                    "participants": war.participants,
                    "alliances": war.alliances,
                    "casualties": war.casualties,
                    "resources_lost": war.resources_lost,
                    "intensity": war.intensity,
                    "duration": war.duration,
                    "resolution": war.resolution,
                    "created_at": war.created_at,
                    "last_update": war.last_update
                }
                for name, war in self.wars.items()
            },
            "institutions": {
                name: {
                    "name": institution.name,
                    "creator": institution.creator,
                    "creation_date": institution.creation_date,
                    "description": institution.description,
                    "purpose": institution.purpose,
                    "members": institution.members,
                    "influence": institution.influence,
                    "created_at": institution.created_at,
                    "last_update": institution.last_update
                }
                for name, institution in self.institutions.items()
            }
        } 