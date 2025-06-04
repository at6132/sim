from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import random
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class InfrastructureType(Enum):
    TRANSPORT = "transport"
    UTILITY = "utility"
    STRUCTURE = "structure"
    NETWORK = "network"
    SERVICE = "service"

@dataclass
class Infrastructure:
    name: str
    type: InfrastructureType
    description: str
    location: Tuple[float, float]
    capacity: float
    efficiency: float = 1.0
    maintenance: float = 1.0
    age: float = 0.0
    connected_to: Set[str] = field(default_factory=set)
    required_resources: Dict[str, float] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent infrastructure
    created_at: float = field(default_factory=time.time)
    last_maintenance: float = field(default_factory=time.time)

@dataclass
class Structure:
    name: str
    type: str  # Emergent structure type
    description: str
    location: Tuple[float, float]
    size: float
    capacity: int
    efficiency: float = 1.0
    maintenance: float = 1.0
    age: float = 0.0
    occupants: Set[str] = field(default_factory=set)
    required_resources: Dict[str, float] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent structures
    created_at: float = field(default_factory=time.time)
    last_maintenance: float = field(default_factory=time.time)

@dataclass
class Network:
    name: str
    type: str  # Emergent network type
    description: str
    nodes: Set[str] = field(default_factory=set)
    connections: Dict[str, Set[str]] = field(default_factory=dict)
    capacity: float = 1.0
    efficiency: float = 1.0
    maintenance: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent networks
    created_at: float = field(default_factory=time.time)
    last_maintenance: float = field(default_factory=time.time)

class InfrastructureSystem:
    def __init__(self, world):
        """Initialize the infrastructure system."""
        self.world = world
        self.infrastructure: Dict[str, Infrastructure] = {}
        self.structures: Dict[str, Structure] = {}
        self.networks: Dict[str, Network] = {}
        self.initialize_system()
        
    def initialize_system(self):
        """Initialize the infrastructure system with minimal structure."""
        logger.info("Initializing infrastructure system...")
        
        # Create a basic network - but don't prescribe its type
        self.networks["main_network"] = Network(
            name="Main Network",
            type="emergent",  # Let the simulation determine the type
            description="Primary infrastructure network"
        )
        
        logger.info("Infrastructure system initialization complete")
        
    def create_infrastructure(self, name: str, type: InfrastructureType, description: str,
                            location: Tuple[float, float], capacity: float,
                            properties: Dict[str, Any] = None,
                            required_resources: Dict[str, float] = None) -> Infrastructure:
        """Create new infrastructure with custom properties."""
        if name in self.infrastructure:
            logger.warning(f"Infrastructure {name} already exists")
            return self.infrastructure[name]
            
        infrastructure = Infrastructure(
            name=name,
            type=type,
            description=description,
            location=location,
            capacity=capacity,
            properties=properties or {},
            required_resources=required_resources or {}
        )
        
        self.infrastructure[name] = infrastructure
        logger.info(f"Created new infrastructure: {name}")
        return infrastructure
        
    def create_structure(self, name: str, type: str, description: str,
                        location: Tuple[float, float], size: float, capacity: int,
                        properties: Dict[str, Any] = None,
                        required_resources: Dict[str, float] = None) -> Structure:
        """Create new structure with custom type and properties."""
        if name in self.structures:
            logger.warning(f"Structure {name} already exists")
            return self.structures[name]
            
        structure = Structure(
            name=name,
            type=type,
            description=description,
            location=location,
            size=size,
            capacity=capacity,
            properties=properties or {},
            required_resources=required_resources or {}
        )
        
        self.structures[name] = structure
        logger.info(f"Created new structure: {name} of type {type}")
        return structure
        
    def create_network(self, name: str, type: str, description: str,
                      properties: Dict[str, Any] = None) -> Network:
        """Create new network with custom type and properties."""
        if name in self.networks:
            logger.warning(f"Network {name} already exists")
            return self.networks[name]
            
        network = Network(
            name=name,
            type=type,
            description=description,
            properties=properties or {}
        )
        
        self.networks[name] = network
        logger.info(f"Created new network: {name} of type {type}")
        return network
        
    def connect_infrastructure(self, network: str, infrastructure: str) -> bool:
        """Connect infrastructure to a network."""
        if network not in self.networks:
            logger.error(f"Network {network} does not exist")
            return False
            
        if infrastructure not in self.infrastructure:
            logger.error(f"Infrastructure {infrastructure} does not exist")
            return False
            
        self.networks[network].nodes.add(infrastructure)
        self.infrastructure[infrastructure].connected_to.add(network)
        
        logger.info(f"Connected {infrastructure} to {network}")
        return True
        
    def add_structure_occupant(self, structure: str, occupant: str) -> bool:
        """Add occupant to a structure."""
        if structure not in self.structures:
            logger.error(f"Structure {structure} does not exist")
            return False
            
        if len(self.structures[structure].occupants) >= self.structures[structure].capacity:
            logger.error(f"Structure {structure} is at capacity")
            return False
            
        self.structures[structure].occupants.add(occupant)
        logger.info(f"Added occupant {occupant} to {structure}")
        return True
        
    def remove_structure_occupant(self, structure: str, occupant: str) -> bool:
        """Remove occupant from a structure."""
        if structure not in self.structures:
            logger.error(f"Structure {structure} does not exist")
            return False
            
        if occupant not in self.structures[structure].occupants:
            logger.error(f"Occupant {occupant} is not in {structure}")
            return False
            
        self.structures[structure].occupants.remove(occupant)
        logger.info(f"Removed occupant {occupant} from {structure}")
        return True
        
    def update_infrastructure(self, time_delta: float):
        """Update infrastructure state."""
        # Let the simulation determine how infrastructure evolves
        self._update_maintenance(time_delta)
        
        # Update network efficiency based on emergent rules
        self._update_network_efficiency(time_delta)
        
        # Update structure states based on emergent rules
        self._update_structures(time_delta)
        
        # Check for emergent infrastructure events
        self._check_infrastructure_events(time_delta)
        
    def _update_maintenance(self, time_delta: float):
        """Update maintenance state of infrastructure."""
        for infrastructure in self.infrastructure.values():
            # Let the simulation determine maintenance needs
            pass
            
    def _update_network_efficiency(self, time_delta: float):
        """Update network efficiency based on emergent rules."""
        for network in self.networks.values():
            # Let the simulation determine efficiency factors
            pass
            
    def _update_structures(self, time_delta: float):
        """Update structure states based on emergent rules."""
        for structure in self.structures.values():
            # Let the simulation determine structure evolution
            pass
            
    def _check_infrastructure_events(self, time_delta: float):
        """Check for emergent infrastructure events."""
        # Let the simulation determine what events occur
        pass
        
    def update(self, time_delta: float):
        """Update infrastructure system state."""
        # Update infrastructure
        self.update_infrastructure(time_delta)
        
        # Update networks
        self._update_network_efficiency(time_delta)
        
        # Update structures
        self._update_structures(time_delta)
        
        # Check for events
        self._check_infrastructure_events(time_delta)
        
    def to_dict(self) -> Dict:
        """Convert infrastructure system state to dictionary for serialization."""
        return {
            "infrastructure": {
                name: {
                    "name": infra.name,
                    "type": infra.type.value,
                    "description": infra.description,
                    "location": infra.location,
                    "capacity": infra.capacity,
                    "efficiency": infra.efficiency,
                    "maintenance": infra.maintenance,
                    "age": infra.age,
                    "connected_to": list(infra.connected_to),
                    "required_resources": infra.required_resources,
                    "properties": infra.properties,
                    "created_at": infra.created_at,
                    "last_maintenance": infra.last_maintenance
                }
                for name, infra in self.infrastructure.items()
            },
            "structures": {
                name: {
                    "name": structure.name,
                    "type": structure.type,
                    "description": structure.description,
                    "location": structure.location,
                    "size": structure.size,
                    "capacity": structure.capacity,
                    "efficiency": structure.efficiency,
                    "maintenance": structure.maintenance,
                    "age": structure.age,
                    "occupants": list(structure.occupants),
                    "required_resources": structure.required_resources,
                    "properties": structure.properties,
                    "created_at": structure.created_at,
                    "last_maintenance": structure.last_maintenance
                }
                for name, structure in self.structures.items()
            },
            "networks": {
                name: {
                    "name": network.name,
                    "type": network.type,
                    "description": network.description,
                    "nodes": list(network.nodes),
                    "connections": {
                        node: list(connections)
                        for node, connections in network.connections.items()
                    },
                    "capacity": network.capacity,
                    "efficiency": network.efficiency,
                    "maintenance": network.maintenance,
                    "properties": network.properties,
                    "created_at": network.created_at,
                    "last_maintenance": network.last_maintenance
                }
                for name, network in self.networks.items()
            }
        } 