from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class Crisis:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    type: str = ""  # Let agents define types
    description: str = ""
    location: Tuple[float, float] = (0.0, 0.0)
    severity: float = 0.0  # 0-1 scale
    duration: float = 0.0  # Time in hours
    affected_agents: Set[str] = field(default_factory=set)  # Set of agent IDs
    affected_resources: List[str] = field(default_factory=list)  # List of resource names
    status: str = "active"  # active, contained, resolved
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Response:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    crisis: str  # Crisis name
    type: str = ""  # Let agents define types
    description: str = ""
    resources_required: Dict[str, float] = field(default_factory=dict)
    effectiveness: float = 0.0  # 0-1 scale
    participants: Set[str] = field(default_factory=set)  # Set of agent IDs
    status: str = "planned"  # planned, active, completed, failed
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class CrisisSystem:
    def __init__(self, world):
        """Initialize the crisis system."""
        self.world = world
        self.crises: Dict[str, Crisis] = {}
        self.responses: Dict[str, Response] = {}
        
    def create_crisis(self, name: str, creator: str,
                     type: str, description: str,
                     location: Tuple[float, float]) -> Crisis:
        """Create a new crisis."""
        if name in self.crises:
            logger.warning(f"Crisis {name} already exists")
            return self.crises[name]
            
        crisis = Crisis(
            name=name,
            creator=creator,
            type=type,
            description=description,
            location=location
        )
        
        self.crises[name] = crisis
        logger.info(f"Created new crisis: {name}")
        return crisis
        
    def create_response(self, name: str, creator: str,
                       crisis: str, type: str,
                       description: str = "") -> Response:
        """Create a new crisis response."""
        if name in self.responses:
            logger.warning(f"Response {name} already exists")
            return self.responses[name]
            
        response = Response(
            name=name,
            creator=creator,
            crisis=crisis,
            type=type,
            description=description
        )
        
        self.responses[name] = response
        logger.info(f"Created new response: {name}")
        return response
        
    def add_affected_agent(self, crisis: str, agent_id: str):
        """Add an affected agent to a crisis."""
        if crisis in self.crises:
            self.crises[crisis].affected_agents.add(agent_id)
            logger.info(f"Added affected agent {agent_id} to crisis {crisis}")
            
    def add_affected_resource(self, crisis: str, resource: str):
        """Add an affected resource to a crisis."""
        if crisis in self.crises:
            self.crises[crisis].affected_resources.append(resource)
            logger.info(f"Added affected resource {resource} to crisis {crisis}")
            
    def add_response_participant(self, response: str, agent_id: str):
        """Add a participant to a crisis response."""
        if response in self.responses:
            self.responses[response].participants.add(agent_id)
            logger.info(f"Added participant {agent_id} to response {response}")
            
    def evolve_crisis(self, name: str, time_delta: float):
        """Evolve a crisis over time."""
        if name not in self.crises:
            return
            
        crisis = self.crises[name]
        
        # Update duration
        crisis.duration += time_delta
        
        # Update severity based on affected agents and resources
        agent_factor = min(1.0, len(crisis.affected_agents) / 100.0)
        resource_factor = min(1.0, len(crisis.affected_resources) / 10.0)
        
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            crisis.severity = min(1.0,
                crisis.severity + (agent_factor * 0.6 + resource_factor * 0.4) * 0.1)
                
        # Check for resolution
        if crisis.severity < 0.2 and random.random() < 0.05 * time_delta:
            crisis.status = "resolved"
            logger.info(f"Crisis {name} resolved")
            
    def evolve_response(self, name: str, time_delta: float):
        """Evolve a crisis response over time."""
        if name not in self.responses:
            return
            
        response = self.responses[name]
        
        if response.status == "active":
            # Update effectiveness based on participants
            participant_factor = min(1.0, len(response.participants) / 10.0)
            response.effectiveness = (response.effectiveness * 0.9 + participant_factor * 0.1)
            
            # Check for completion
            if response.effectiveness > 0.8:
                response.status = "completed"
                logger.info(f"Response {name} completed")
                
            # Check for failure
            elif response.effectiveness < 0.2 and random.random() < 0.1 * time_delta:
                response.status = "failed"
                logger.info(f"Response {name} failed")
                
    def update(self, time_delta: float):
        """Update crisis system state."""
        # Evolve crises
        for name in list(self.crises.keys()):
            self.evolve_crisis(name, time_delta)
            
        # Evolve responses
        for name in list(self.responses.keys()):
            self.evolve_response(name, time_delta)
            
    def to_dict(self) -> Dict:
        """Convert crisis system state to dictionary for serialization."""
        return {
            "crises": {
                name: {
                    "name": crisis.name,
                    "creator": crisis.creator,
                    "creation_date": crisis.creation_date,
                    "type": crisis.type,
                    "description": crisis.description,
                    "location": crisis.location,
                    "severity": crisis.severity,
                    "duration": crisis.duration,
                    "affected_agents": list(crisis.affected_agents),
                    "affected_resources": crisis.affected_resources,
                    "status": crisis.status,
                    "created_at": crisis.created_at,
                    "last_update": crisis.last_update
                }
                for name, crisis in self.crises.items()
            },
            "responses": {
                name: {
                    "name": response.name,
                    "creator": response.creator,
                    "creation_date": response.creation_date,
                    "crisis": response.crisis,
                    "type": response.type,
                    "description": response.description,
                    "resources_required": response.resources_required,
                    "effectiveness": response.effectiveness,
                    "participants": list(response.participants),
                    "status": response.status,
                    "created_at": response.created_at,
                    "last_update": response.last_update
                }
                for name, response in self.responses.items()
            }
        } 