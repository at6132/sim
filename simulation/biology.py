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
class Organism:
    name: str
    type: str  # Emergent organism type
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent traits
    adaptations: Dict[str, Any] = field(default_factory=dict)  # Evolved adaptations
    interactions: Dict[str, Any] = field(default_factory=dict)  # Interaction patterns
    created_at: float = field(default_factory=time.time)
    last_adaptation: float = field(default_factory=time.time)

@dataclass
class Ecosystem:
    name: str
    type: str  # Emergent ecosystem type
    description: str
    organisms: Dict[str, Organism] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent ecosystems
    interactions: Dict[str, Any] = field(default_factory=dict)  # Ecosystem-level interactions
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Adaptation:
    name: str
    type: str  # Emergent adaptation type
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent adaptations
    requirements: Dict[str, Any] = field(default_factory=dict)  # Requirements for adaptation
    effects: Dict[str, Any] = field(default_factory=dict)  # Effects of adaptation
    created_at: float = field(default_factory=time.time)

class BiologicalSystem:
    def __init__(self, world):
        """Initialize the biological system."""
        self.world = world
        self.organisms: Dict[str, Organism] = {}
        self.ecosystems: Dict[str, Ecosystem] = {}
        self.adaptations: Dict[str, Adaptation] = {}
        self.initialize_system()
        
    def initialize_system(self):
        """Initialize the biological system with minimal structure."""
        logger.info("Initializing biological system...")
        
        # Create a basic ecosystem - but don't prescribe its type
        self.ecosystems["main_ecosystem"] = Ecosystem(
            name="Main Ecosystem",
            type="emergent",  # Let the simulation determine the type
            description="Primary biological environment"
        )
        
        logger.info("Biological system initialization complete")
        
    def create_organism(self, name: str, type: str, description: str,
                       properties: Dict[str, Any] = None) -> Organism:
        """Create new organism with custom properties."""
        if name in self.organisms:
            logger.warning(f"Organism {name} already exists")
            return self.organisms[name]
            
        organism = Organism(
            name=name,
            type=type,
            description=description,
            properties=properties or {}
        )
        
        self.organisms[name] = organism
        logger.info(f"Created new organism: {name} of type {type}")
        return organism
        
    def create_ecosystem(self, name: str, type: str, description: str,
                        properties: Dict[str, Any] = None) -> Ecosystem:
        """Create new ecosystem with custom type and properties."""
        if name in self.ecosystems:
            logger.warning(f"Ecosystem {name} already exists")
            return self.ecosystems[name]
            
        ecosystem = Ecosystem(
            name=name,
            type=type,
            description=description,
            properties=properties or {}
        )
        
        self.ecosystems[name] = ecosystem
        logger.info(f"Created new ecosystem: {name} of type {type}")
        return ecosystem
        
    def create_adaptation(self, name: str, type: str, description: str,
                         properties: Dict[str, Any] = None,
                         requirements: Dict[str, Any] = None,
                         effects: Dict[str, Any] = None) -> Adaptation:
        """Create new adaptation with custom properties."""
        if name in self.adaptations:
            logger.warning(f"Adaptation {name} already exists")
            return self.adaptations[name]
            
        adaptation = Adaptation(
            name=name,
            type=type,
            description=description,
            properties=properties or {},
            requirements=requirements or {},
            effects=effects or {}
        )
        
        self.adaptations[name] = adaptation
        logger.info(f"Created new adaptation: {name} of type {type}")
        return adaptation
        
    def add_organism_to_ecosystem(self, ecosystem: str, organism: str) -> bool:
        """Add organism to an ecosystem."""
        if ecosystem not in self.ecosystems:
            logger.error(f"Ecosystem {ecosystem} does not exist")
            return False
            
        if organism not in self.organisms:
            logger.error(f"Organism {organism} does not exist")
            return False
            
        self.ecosystems[ecosystem].organisms[organism] = self.organisms[organism]
        logger.info(f"Added organism {organism} to ecosystem {ecosystem}")
        return True
        
    def update_organisms(self, time_delta: float):
        """Update organism states."""
        # Let the simulation determine how organisms evolve
        self._update_adaptations(time_delta)
        
        # Update interactions based on emergent rules
        self._update_interactions(time_delta)
        
        # Check for emergent biological events
        self._check_biological_events(time_delta)
        
    def _update_adaptations(self, time_delta: float):
        """Update organism adaptations based on emergent rules."""
        if not self.adaptations:
            return

        for organism in self.organisms.values():
            # Chance to gain a new adaptation over time
            if random.random() < 0.05 * time_delta:
                adaptation = random.choice(list(self.adaptations.values()))
                if adaptation.name not in organism.adaptations:
                    organism.adaptations[adaptation.name] = adaptation.properties.copy()
                    organism.last_adaptation = time.time()
                    logger.info(
                        f"{organism.name} acquired adaptation {adaptation.name}"
                    )

            # Existing adaptations drift slightly
            for adapt_name, props in organism.adaptations.items():
                for prop, value in list(props.items()):
                    if isinstance(value, (int, float)):
                        props[prop] = value * (
                            1 + random.uniform(-0.01, 0.01) * time_delta
                        )
            
    def _update_interactions(self, time_delta: float):
        """Update organism interactions based on emergent rules."""
        for ecosystem in self.ecosystems.values():
            orgs = list(ecosystem.organisms.keys())
            for i in range(len(orgs)):
                for j in range(i + 1, len(orgs)):
                    pair = f"{orgs[i]}-{orgs[j]}"
                    interaction = ecosystem.interactions.setdefault(
                        pair,
                        {"strength": random.random(), "last": time.time()},
                    )

                    change = random.uniform(-0.02, 0.02) * time_delta
                    interaction["strength"] = max(
                        0.0, min(1.0, interaction["strength"] + change)
                    )
                    interaction["last"] = time.time()

            # Remove very weak interactions
            to_remove = [
                k for k, v in ecosystem.interactions.items() if v["strength"] <= 0
            ]
            for k in to_remove:
                del ecosystem.interactions[k]
            
    def _check_biological_events(self, time_delta: float):
        """Check for emergent biological events."""
        for name, organism in list(self.organisms.items()):
            # Small chance an organism dies out
            if random.random() < 0.001 * time_delta:
                logger.info(f"Organism {name} died out")
                del self.organisms[name]
                for eco in self.ecosystems.values():
                    eco.organisms.pop(name, None)

        # Random spontaneous adaptation creation
        if self.organisms and self.adaptations:
            if random.random() < 0.002 * time_delta:
                org = random.choice(list(self.organisms.values()))
                adaptation = random.choice(list(self.adaptations.values()))
                if adaptation.name not in org.adaptations:
                    org.adaptations[adaptation.name] = adaptation.properties.copy()
                    org.last_adaptation = time.time()
                    logger.info(
                        f"Biological event: {org.name} spontaneously developed {adaptation.name}"
                    )
        
    def update(self, time_delta: float):
        """Update biological system state."""
        # Update organisms
        self.update_organisms(time_delta)
        
        # Update ecosystems
        self._update_interactions(time_delta)
        
        # Check for events
        self._check_biological_events(time_delta)
        
    def to_dict(self) -> Dict:
        """Convert biological system state to dictionary for serialization."""
        return {
            "organisms": {
                name: {
                    "name": org.name,
                    "type": org.type,
                    "description": org.description,
                    "properties": org.properties,
                    "adaptations": org.adaptations,
                    "interactions": org.interactions,
                    "created_at": org.created_at,
                    "last_adaptation": org.last_adaptation
                }
                for name, org in self.organisms.items()
            },
            "ecosystems": {
                name: {
                    "name": eco.name,
                    "type": eco.type,
                    "description": eco.description,
                    "organisms": {
                        org_name: {
                            "name": org.name,
                            "type": org.type,
                            "properties": org.properties
                        }
                        for org_name, org in eco.organisms.items()
                    },
                    "properties": eco.properties,
                    "interactions": eco.interactions,
                    "created_at": eco.created_at,
                    "last_update": eco.last_update
                }
                for name, eco in self.ecosystems.items()
            },
            "adaptations": {
                name: {
                    "name": adapt.name,
                    "type": adapt.type,
                    "description": adapt.description,
                    "properties": adapt.properties,
                    "requirements": adapt.requirements,
                    "effects": adapt.effects,
                    "created_at": adapt.created_at
                }
                for name, adapt in self.adaptations.items()
            }
        } 