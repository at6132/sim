from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

class ThoughtType(Enum):
    OBSERVATION = "observation"
    REASONING = "reasoning"
    MEMORY = "memory"
    EMOTION = "emotion"
    DECISION = "decision"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"

@dataclass
class Thought:
    type: str  # Emergent thought type
    content: Any
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent thoughts
    connections: Dict[str, Any] = field(default_factory=dict)  # Connections to other thoughts
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)

@dataclass
class Memory:
    type: str  # Emergent memory type
    content: Any
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent memories
    associations: Dict[str, Any] = field(default_factory=dict)  # Memory associations
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)

@dataclass
class Learning:
    type: str  # Emergent learning type
    content: Any
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent learning
    applications: Dict[str, Any] = field(default_factory=dict)  # Learning applications
    created_at: float = field(default_factory=time.time)
    last_applied: float = field(default_factory=time.time)

class CognitiveSystem:
    def __init__(self, world):
        """Initialize the cognitive system."""
        self.world = world
        self.thoughts: Dict[str, Thought] = {}
        self.memories: Dict[str, Memory] = {}
        self.learning: Dict[str, Learning] = {}
        self.initialize_system()
        
    def initialize_system(self):
        """Initialize the cognitive system with minimal structure."""
        logger.info("Initializing cognitive system...")
        
        # Create a basic thought - but don't prescribe its type
        self.thoughts["initial_thought"] = Thought(
            type="emergent",  # Let the simulation determine the type
            content="Initial cognitive state"
        )
        
        logger.info("Cognitive system initialization complete")
        
    def create_thought(self, type: str, content: Any,
                      properties: Dict[str, Any] = None) -> Thought:
        """Create new thought with custom properties."""
        thought = Thought(
            type=type,
            content=content,
            properties=properties or {}
        )
        
        thought_id = f"thought_{len(self.thoughts)}"
        self.thoughts[thought_id] = thought
        logger.info(f"Created new thought of type {type}")
        return thought
        
    def create_memory(self, type: str, content: Any,
                     properties: Dict[str, Any] = None) -> Memory:
        """Create new memory with custom properties."""
        memory = Memory(
            type=type,
            content=content,
            properties=properties or {}
        )
        
        memory_id = f"memory_{len(self.memories)}"
        self.memories[memory_id] = memory
        logger.info(f"Created new memory of type {type}")
        return memory
        
    def create_learning(self, type: str, content: Any,
                       properties: Dict[str, Any] = None) -> Learning:
        """Create new learning with custom properties."""
        learning = Learning(
            type=type,
            content=content,
            properties=properties or {}
        )
        
        learning_id = f"learning_{len(self.learning)}"
        self.learning[learning_id] = learning
        logger.info(f"Created new learning of type {type}")
        return learning
        
    def connect_thoughts(self, thought1: str, thought2: str,
                        connection_type: str, properties: Dict[str, Any] = None) -> bool:
        """Connect two thoughts with custom properties."""
        if thought1 not in self.thoughts or thought2 not in self.thoughts:
            logger.error("One or both thoughts do not exist")
            return False
            
        self.thoughts[thought1].connections[thought2] = {
            "type": connection_type,
            "properties": properties or {}
        }
        
        self.thoughts[thought2].connections[thought1] = {
            "type": connection_type,
            "properties": properties or {}
        }
        
        logger.info(f"Connected thoughts {thought1} and {thought2}")
        return True
        
    def associate_memories(self, memory1: str, memory2: str,
                          association_type: str, properties: Dict[str, Any] = None) -> bool:
        """Associate two memories with custom properties."""
        if memory1 not in self.memories or memory2 not in self.memories:
            logger.error("One or both memories do not exist")
            return False
            
        self.memories[memory1].associations[memory2] = {
            "type": association_type,
            "properties": properties or {}
        }
        
        self.memories[memory2].associations[memory1] = {
            "type": association_type,
            "properties": properties or {}
        }
        
        logger.info(f"Associated memories {memory1} and {memory2}")
        return True
        
    def apply_learning(self, learning: str, application: str,
                      properties: Dict[str, Any] = None) -> bool:
        """Apply learning with custom properties."""
        if learning not in self.learning:
            logger.error(f"Learning {learning} does not exist")
            return False
            
        self.learning[learning].applications[application] = {
            "properties": properties or {},
            "applied_at": time.time()
        }
        
        logger.info(f"Applied learning {learning} to {application}")
        return True
        
    def update_cognition(self, time_delta: float):
        """Update cognitive state."""
        # Let the simulation determine how thoughts evolve
        self._update_thoughts(time_delta)
        
        # Update memories based on emergent rules
        self._update_memories(time_delta)
        
        # Update learning based on emergent rules
        self._update_learning(time_delta)
        
        # Check for emergent cognitive events
        self._check_cognitive_events(time_delta)
        
    def _update_thoughts(self, time_delta: float):
        """Update thoughts based on emergent rules."""
        for thought in self.thoughts.values():
            # Let the simulation determine thought evolution
            pass
            
    def _update_memories(self, time_delta: float):
        """Update memories based on emergent rules."""
        for memory in self.memories.values():
            # Let the simulation determine memory evolution
            pass
            
    def _update_learning(self, time_delta: float):
        """Update learning based on emergent rules."""
        for learning in self.learning.values():
            # Let the simulation determine learning evolution
            pass
            
    def _check_cognitive_events(self, time_delta: float):
        """Check for emergent cognitive events."""
        # Let the simulation determine what events occur
        pass
        
    def update(self, time_delta: float):
        """Update cognitive system state."""
        # Update thoughts
        self._update_thoughts(time_delta)
        
        # Update memories
        self._update_memories(time_delta)
        
        # Update learning
        self._update_learning(time_delta)
        
        # Check for events
        self._check_cognitive_events(time_delta)
        
    def to_dict(self) -> Dict:
        """Convert cognitive system state to dictionary for serialization."""
        return {
            "thoughts": {
                thought_id: {
                    "type": thought.type,
                    "content": thought.content,
                    "properties": thought.properties,
                    "connections": thought.connections,
                    "created_at": thought.created_at,
                    "last_accessed": thought.last_accessed
                }
                for thought_id, thought in self.thoughts.items()
            },
            "memories": {
                memory_id: {
                    "type": memory.type,
                    "content": memory.content,
                    "properties": memory.properties,
                    "associations": memory.associations,
                    "created_at": memory.created_at,
                    "last_accessed": memory.last_accessed
                }
                for memory_id, memory in self.memories.items()
            },
            "learning": {
                learning_id: {
                    "type": learning.type,
                    "content": learning.content,
                    "properties": learning.properties,
                    "applications": learning.applications,
                    "created_at": learning.created_at,
                    "last_applied": learning.last_applied
                }
                for learning_id, learning in self.learning.items()
            }
        } 