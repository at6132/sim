from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import random
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

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

class SocialSystem:
    def __init__(self, world):
        """Initialize the social system."""
        self.world = world
        self.structures: Dict[str, SocialStructure] = {}
        self.interactions: Dict[str, SocialInteraction] = {}
        self.norms: Dict[str, SocialNorm] = {}
        self.initialize_system()
        
    def initialize_system(self):
        """Initialize the social system with minimal structure."""
        logger.info("Initializing social system...")
        
        # Create a basic social structure - but don't prescribe its type
        self.structures["initial_structure"] = SocialStructure(
            type="emergent",  # Let the simulation determine the type
            name="Initial Structure",
            description="Primary social organization"
        )
        
        logger.info("Social system initialization complete")
        
    def create_structure(self, type: str, name: str, description: str,
                        properties: Dict[str, Any] = None) -> SocialStructure:
        """Create new social structure with custom properties."""
        structure = SocialStructure(
            type=type,
            name=name,
            description=description,
            properties=properties or {}
        )
        
        structure_id = f"structure_{len(self.structures)}"
        self.structures[structure_id] = structure
        logger.info(f"Created new social structure: {name} of type {type}")
        return structure
        
    def create_interaction(self, type: str, participants: Dict[str, Any],
                          properties: Dict[str, Any] = None) -> SocialInteraction:
        """Create new social interaction with custom properties."""
        interaction = SocialInteraction(
            type=type,
            participants=participants,
            properties=properties or {}
        )
        
        interaction_id = f"interaction_{len(self.interactions)}"
        self.interactions[interaction_id] = interaction
        logger.info(f"Created new social interaction of type {type}")
        return interaction
        
    def create_norm(self, type: str, description: str,
                   properties: Dict[str, Any] = None,
                   conditions: Dict[str, Any] = None,
                   consequences: Dict[str, Any] = None) -> SocialNorm:
        """Create new social norm with custom properties."""
        norm = SocialNorm(
            type=type,
            description=description,
            properties=properties or {},
            conditions=conditions or {},
            consequences=consequences or {}
        )
        
        norm_id = f"norm_{len(self.norms)}"
        self.norms[norm_id] = norm
        logger.info(f"Created new social norm of type {type}")
        return norm
        
    def add_member_to_structure(self, structure: str, member: str,
                              properties: Dict[str, Any] = None) -> bool:
        """Add member to a social structure with custom properties."""
        if structure not in self.structures:
            logger.error(f"Structure {structure} does not exist")
            return False
            
        self.structures[structure].members[member] = properties or {}
        logger.info(f"Added member {member} to structure {structure}")
        return True
        
    def update_structures(self, time_delta: float):
        """Update social structures."""
        # Let the simulation determine how structures evolve
        self._update_structure_interactions(time_delta)
        
        # Update member relationships based on emergent rules
        self._update_member_relationships(time_delta)
        
        # Check for emergent social events
        self._check_social_events(time_delta)
        
    def _update_structure_interactions(self, time_delta: float):
        """Update structure interactions based on emergent rules."""
        for structure in self.structures.values():
            # Let the simulation determine interaction patterns
            pass
            
    def _update_member_relationships(self, time_delta: float):
        """Update member relationships based on emergent rules."""
        for structure in self.structures.values():
            # Let the simulation determine relationship evolution
            pass
            
    def _check_social_events(self, time_delta: float):
        """Check for emergent social events."""
        # Let the simulation determine what events occur
        pass
        
    def update(self, time_delta: float):
        """Update social system state."""
        # Update structures
        self.update_structures(time_delta)
        
        # Update interactions
        self._update_structure_interactions(time_delta)
        
        # Check for events
        self._check_social_events(time_delta)
        
    def to_dict(self) -> Dict:
        """Convert social system state to dictionary for serialization."""
        return {
            "structures": {
                structure_id: {
                    "type": structure.type,
                    "name": structure.name,
                    "description": structure.description,
                    "properties": structure.properties,
                    "members": structure.members,
                    "interactions": structure.interactions,
                    "created_at": structure.created_at,
                    "last_update": structure.last_update
                }
                for structure_id, structure in self.structures.items()
            },
            "interactions": {
                interaction_id: {
                    "type": interaction.type,
                    "participants": interaction.participants,
                    "properties": interaction.properties,
                    "effects": interaction.effects,
                    "created_at": interaction.created_at,
                    "last_occurred": interaction.last_occurred
                }
                for interaction_id, interaction in self.interactions.items()
            },
            "norms": {
                norm_id: {
                    "type": norm.type,
                    "description": norm.description,
                    "properties": norm.properties,
                    "conditions": norm.conditions,
                    "consequences": norm.consequences,
                    "created_at": norm.created_at
                }
                for norm_id, norm in self.norms.items()
            }
        } 