from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class SocialStructure:
    type: str  # Emergent social structure type
    name: str
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent structures
    members: Dict[str, Any] = field(default_factory=dict)  # Member relationships
    interactions: Dict[str, Any] = field(default_factory=dict)  # Structure-level interactions
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class SocialInteraction:
    type: str  # Emergent interaction type
    participants: Dict[str, Any]  # Participant relationships
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent interactions
    effects: Dict[str, Any] = field(default_factory=dict)  # Interaction effects
    created_at: float = field(default_factory=time.time)
    last_occurred: float = field(default_factory=time.time)

@dataclass
class SocialNorm:
    type: str  # Emergent norm type
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent norms
    conditions: Dict[str, Any] = field(default_factory=dict)  # Conditions for norm application
    consequences: Dict[str, Any] = field(default_factory=dict)  # Consequences of norm violation
    created_at: float = field(default_factory=time.time)

class Social:
    def __init__(self, world):
        self.world = world
        self.logger = get_logger(__name__)
        
        # Initialize social components
        self.relationships = {}  # relationship_id -> Relationship
        self.groups = {}  # group_id -> Group
        self.traditions = {}  # tradition_id -> Tradition
        self.beliefs = {}  # belief_id -> Belief
        self.customs = {}  # custom_id -> Custom
        
        self.logger.info("Social system initialized")
    
    def initialize_social(self):
        """Initialize the social system with basic structures."""
        self.logger.info("Initializing social system...")
        
        # Initialize relationships
        self._initialize_relationships()
        
        # Initialize groups
        self._initialize_groups()
        
        # Initialize traditions
        self._initialize_traditions()
        
        # Initialize beliefs
        self._initialize_beliefs()
        
        # Initialize customs
        self._initialize_customs()
        
        self.logger.info("Social system initialization complete")
    
    def _initialize_relationships(self):
        """Initialize basic relationships."""
        self.logger.info("Initializing relationships...")
        
        # Define basic relationship types
        basic_relationships = {
            "family": {
                "name": "Family",
                "type": "kinship",
                "strength": 0.8,
                "trust": 0.9,
                "loyalty": 0.9
            },
            "friend": {
                "name": "Friend",
                "type": "social",
                "strength": 0.6,
                "trust": 0.7,
                "loyalty": 0.6
            },
            "ally": {
                "name": "Ally",
                "type": "political",
                "strength": 0.7,
                "trust": 0.6,
                "loyalty": 0.7
            }
        }
        
        # Add relationships to system
        for relationship_id, relationship_data in basic_relationships.items():
            self.relationships[relationship_id] = relationship_data
            self.logger.info(f"Added relationship: {relationship_data['name']}")
    
    def _initialize_groups(self):
        """Initialize basic social groups."""
        self.logger.info("Initializing social groups...")
        
        # Define basic group types
        basic_groups = {
            "family": {
                "name": "Family Group",
                "type": "kinship",
                "size": 4,
                "cohesion": 0.8,
                "hierarchy": "patriarchal"
            },
            "tribe": {
                "name": "Tribe",
                "type": "social",
                "size": 50,
                "cohesion": 0.6,
                "hierarchy": "council"
            },
            "clan": {
                "name": "Clan",
                "type": "kinship",
                "size": 100,
                "cohesion": 0.7,
                "hierarchy": "elders"
            }
        }
        
        # Add groups to system
        for group_id, group_data in basic_groups.items():
            self.groups[group_id] = group_data
            self.logger.info(f"Added group: {group_data['name']}")
    
    def _initialize_traditions(self):
        """Initialize basic traditions."""
        self.logger.info("Initializing traditions...")
        
        # Define basic traditions
        basic_traditions = {
            "coming_of_age": {
                "name": "Coming of Age",
                "type": "ritual",
                "importance": 0.8,
                "frequency": "once",
                "participants": "youth"
            },
            "harvest_festival": {
                "name": "Harvest Festival",
                "type": "celebration",
                "importance": 0.7,
                "frequency": "yearly",
                "participants": "all"
            },
            "ancestor_worship": {
                "name": "Ancestor Worship",
                "type": "religious",
                "importance": 0.9,
                "frequency": "monthly",
                "participants": "family"
            }
        }
        
        # Add traditions to system
        for tradition_id, tradition_data in basic_traditions.items():
            self.traditions[tradition_id] = tradition_data
            self.logger.info(f"Added tradition: {tradition_data['name']}")
    
    def _initialize_beliefs(self):
        """Initialize basic beliefs."""
        self.logger.info("Initializing beliefs...")
        
        # Define basic beliefs
        basic_beliefs = {
            "nature_spirits": {
                "name": "Nature Spirits",
                "type": "spiritual",
                "strength": 0.7,
                "followers": 0.6
            },
            "ancestral_guidance": {
                "name": "Ancestral Guidance",
                "type": "spiritual",
                "strength": 0.8,
                "followers": 0.7
            },
            "tribal_unity": {
                "name": "Tribal Unity",
                "type": "social",
                "strength": 0.9,
                "followers": 0.8
            }
        }
        
        # Add beliefs to system
        for belief_id, belief_data in basic_beliefs.items():
            self.beliefs[belief_id] = belief_data
            self.logger.info(f"Added belief: {belief_data['name']}")
    
    def _initialize_customs(self):
        """Initialize basic customs."""
        self.logger.info("Initializing customs...")
        
        # Define basic customs
        basic_customs = {
            "greeting": {
                "name": "Greeting Custom",
                "type": "social",
                "frequency": "daily",
                "importance": 0.6
            },
            "sharing": {
                "name": "Sharing Custom",
                "type": "economic",
                "frequency": "weekly",
                "importance": 0.8
            },
            "hospitality": {
                "name": "Hospitality Custom",
                "type": "social",
                "frequency": "as_needed",
                "importance": 0.7
            }
        }
        
        # Add customs to system
        for custom_id, custom_data in basic_customs.items():
            self.customs[custom_id] = custom_data
            self.logger.info(f"Added custom: {custom_data['name']}")
    
    def update(self, time_delta: float):
        """Update the social system state."""
        self.logger.debug(f"Updating social system with time delta: {time_delta}")
        
        # Update relationships
        self._update_relationships(time_delta)
        
        # Update groups
        self._update_groups(time_delta)
        
        # Update traditions
        self._update_traditions(time_delta)
        
        # Update beliefs
        self._update_beliefs(time_delta)
        
        # Update customs
        self._update_customs(time_delta)
        
        self.logger.debug("Social system update complete")
    
    def _update_relationships(self, time_delta: float):
        """Update relationship states."""
        for relationship_id, relationship in self.relationships.items():
            # Update relationship strength
            if "strength" in relationship:
                # Relationships strengthen or weaken over time
                change_rate = 0.001 * time_delta  # 0.1% per hour
                relationship["strength"] = max(0.0, min(1.0, relationship["strength"] + change_rate))
                
                # Update trust and loyalty based on strength
                relationship["trust"] = max(0.0, min(1.0, relationship["strength"] * 0.9))
                relationship["loyalty"] = max(0.0, min(1.0, relationship["strength"] * 0.8))
    
    def _update_groups(self, time_delta: float):
        """Update group states."""
        for group_id, group in self.groups.items():
            # Update group cohesion
            if "cohesion" in group:
                # Group cohesion changes over time
                change_rate = 0.0005 * time_delta  # 0.05% per hour
                group["cohesion"] = max(0.0, min(1.0, group["cohesion"] + change_rate))
                
                # Update group size based on cohesion
                if "size" in group:
                    growth_rate = 0.0001 * time_delta * group["cohesion"]  # 0.01% per hour
                    group["size"] = max(1, int(group["size"] * (1 + growth_rate)))
    
    def _update_traditions(self, time_delta: float):
        """Update tradition states."""
        for tradition_id, tradition in self.traditions.items():
            # Update tradition importance
            if "importance" in tradition:
                # Tradition importance changes over time
                change_rate = 0.0002 * time_delta  # 0.02% per hour
                tradition["importance"] = max(0.0, min(1.0, tradition["importance"] + change_rate))
    
    def _update_beliefs(self, time_delta: float):
        """Update belief states."""
        for belief_id, belief in self.beliefs.items():
            # Update belief strength
            if "strength" in belief:
                # Belief strength changes over time
                change_rate = 0.0003 * time_delta  # 0.03% per hour
                belief["strength"] = max(0.0, min(1.0, belief["strength"] + change_rate))
                
                # Update followers based on strength
                if "followers" in belief:
                    belief["followers"] = max(0.0, min(1.0, belief["strength"] * 0.9))
    
    def _update_customs(self, time_delta: float):
        """Update custom states."""
        for custom_id, custom in self.customs.items():
            # Update custom importance
            if "importance" in custom:
                # Custom importance changes over time
                change_rate = 0.0004 * time_delta  # 0.04% per hour
                custom["importance"] = max(0.0, min(1.0, custom["importance"] + change_rate))
    
    def get_state(self) -> Dict:
        """Get the current state of the social system."""
        return {
            'relationships': self.relationships,
            'groups': self.groups,
            'traditions': self.traditions,
            'beliefs': self.beliefs,
            'customs': self.customs
        } 