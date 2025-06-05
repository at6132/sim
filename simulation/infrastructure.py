from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)


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
    properties: Dict[str, Any] = field(
        default_factory=dict
    )  # Custom properties for emergent infrastructure
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
    properties: Dict[str, Any] = field(
        default_factory=dict
    )  # Custom properties for emergent structures
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
    properties: Dict[str, Any] = field(
        default_factory=dict
    )  # Custom properties for emergent networks
    created_at: float = field(default_factory=time.time)
    last_maintenance: float = field(default_factory=time.time)


class InfrastructureSystem:
    def __init__(self, world):
        """Initialize the infrastructure system."""
        self.world = world
        self.logger = get_logger(__name__)

        # Initialize infrastructure components
        self.buildings = {}  # building_id -> Building
        self.roads = {}  # road_id -> Road
        self.water_systems = {}  # system_id -> WaterSystem
        self.power_systems = {}  # system_id -> PowerSystem
        self.storage_facilities = {}  # facility_id -> StorageFacility

        self.logger.info("Infrastructure system initialized")

    def initialize_infrastructure(self):
        """Initialize the infrastructure system with basic structures."""
        self.logger.info("Initializing infrastructure system...")

        # Initialize buildings
        self._initialize_buildings()

        # Initialize roads
        self._initialize_roads()

        # Initialize water systems
        self._initialize_water_systems()

        # Initialize power systems
        self._initialize_power_systems()

        # Initialize storage facilities
        self._initialize_storage_facilities()

        self.logger.info("Infrastructure system initialization complete")

    def _initialize_buildings(self):
        """Initialize basic buildings."""
        self.logger.info("Initializing buildings...")

        # Define basic building types
        basic_buildings = {
            "hut": {
                "name": "Basic Hut",
                "type": "residential",
                "capacity": 4,
                "durability": 0.5,
                "resources_needed": {"wood": 10, "stone": 5, "thatched_roof": 1},
            },
            "storage_hut": {
                "name": "Storage Hut",
                "type": "storage",
                "capacity": 100,
                "durability": 0.6,
                "resources_needed": {"wood": 15, "stone": 8, "thatched_roof": 1},
            },
            "workshop": {
                "name": "Basic Workshop",
                "type": "industrial",
                "capacity": 2,
                "durability": 0.7,
                "resources_needed": {"wood": 20, "stone": 15, "thatched_roof": 1},
            },
        }

        # Add buildings to system
        for building_id, building_data in basic_buildings.items():
            self.buildings[building_id] = building_data
            self.logger.info(f"Added building: {building_data['name']}")

    def _initialize_roads(self):
        """Initialize basic roads."""
        self.logger.info("Initializing roads...")

        # Define basic road types
        basic_roads = {
            "dirt_path": {
                "name": "Dirt Path",
                "type": "basic",
                "durability": 0.3,
                "speed_modifier": 0.8,
                "resources_needed": {"dirt": 1},
            },
            "stone_road": {
                "name": "Stone Road",
                "type": "improved",
                "durability": 0.7,
                "speed_modifier": 1.2,
                "resources_needed": {"stone": 1, "gravel": 1},
            },
        }

        # Add roads to system
        for road_id, road_data in basic_roads.items():
            self.roads[road_id] = road_data
            self.logger.info(f"Added road: {road_data['name']}")

    def _initialize_water_systems(self):
        """Initialize basic water systems."""
        self.logger.info("Initializing water systems...")

        # Define basic water system types
        basic_water_systems = {
            "well": {
                "name": "Basic Well",
                "type": "water_source",
                "capacity": 100,
                "durability": 0.6,
                "resources_needed": {"stone": 20, "wood": 10},
            },
            "irrigation": {
                "name": "Basic Irrigation",
                "type": "water_distribution",
                "capacity": 50,
                "durability": 0.5,
                "resources_needed": {"wood": 15, "stone": 5},
            },
        }

        # Add water systems to system
        for system_id, system_data in basic_water_systems.items():
            self.water_systems[system_id] = system_data
            self.logger.info(f"Added water system: {system_data['name']}")

    def _initialize_power_systems(self):
        """Initialize basic power systems."""
        self.logger.info("Initializing power systems...")

        # Define basic power system types
        basic_power_systems = {
            "fire_pit": {
                "name": "Fire Pit",
                "type": "basic",
                "capacity": 10,
                "durability": 0.4,
                "resources_needed": {"stone": 5, "wood": 3},
            },
            "torch": {
                "name": "Torch",
                "type": "portable",
                "capacity": 5,
                "durability": 0.3,
                "resources_needed": {"wood": 1, "cloth": 1},
            },
        }

        # Add power systems to system
        for system_id, system_data in basic_power_systems.items():
            self.power_systems[system_id] = system_data
            self.logger.info(f"Added power system: {system_data['name']}")

    def _initialize_storage_facilities(self):
        """Initialize basic storage facilities."""
        self.logger.info("Initializing storage facilities...")

        # Define basic storage facility types
        basic_storage = {
            "basket": {
                "name": "Storage Basket",
                "type": "portable",
                "capacity": 20,
                "durability": 0.4,
                "resources_needed": {"wood": 2, "fiber": 1},
            },
            "chest": {
                "name": "Storage Chest",
                "type": "fixed",
                "capacity": 50,
                "durability": 0.7,
                "resources_needed": {"wood": 5, "metal": 2},
            },
        }

        # Add storage facilities to system
        for facility_id, facility_data in basic_storage.items():
            self.storage_facilities[facility_id] = facility_data
            self.logger.info(f"Added storage facility: {facility_data['name']}")

    def update(self, time_delta: float):
        """Update the infrastructure system state."""
        self.logger.debug(
            f"Updating infrastructure system with time delta: {time_delta}"
        )

        # Update buildings
        self._update_buildings(time_delta)

        # Update roads
        self._update_roads(time_delta)

        # Update water systems
        self._update_water_systems(time_delta)

        # Update power systems
        self._update_power_systems(time_delta)

        # Update storage facilities
        self._update_storage_facilities(time_delta)

        self.logger.debug("Infrastructure system update complete")

    def _update_buildings(self, time_delta: float):
        """Update building states."""
        for building_id, building in self.buildings.items():
            # Update building condition
            if "condition" in building:
                # Buildings deteriorate over time
                deterioration_rate = 0.001 * time_delta  # 0.1% per hour
                building["condition"] = max(
                    0.0, building["condition"] - deterioration_rate
                )

                # Check for critical condition
                if building["condition"] < 0.2:
                    self.logger.warning(
                        f"Building {building['name']} is in critical condition"
                    )

    def _update_roads(self, time_delta: float):
        """Update road states."""
        for road_id, road in self.roads.items():
            # Update road condition
            if "condition" in road:
                # Roads deteriorate over time
                deterioration_rate = 0.002 * time_delta  # 0.2% per hour
                road["condition"] = max(0.0, road["condition"] - deterioration_rate)

                # Check for critical condition
                if road["condition"] < 0.2:
                    self.logger.warning(f"Road {road['name']} is in critical condition")

    def _update_water_systems(self, time_delta: float):
        """Update water system states."""
        for system_id, system in self.water_systems.items():
            # Update system condition
            if "condition" in system:
                # Water systems deteriorate over time
                deterioration_rate = 0.0015 * time_delta  # 0.15% per hour
                system["condition"] = max(0.0, system["condition"] - deterioration_rate)

                # Check for critical condition
                if system["condition"] < 0.2:
                    self.logger.warning(
                        f"Water system {system['name']} is in critical condition"
                    )

    def _update_power_systems(self, time_delta: float):
        """Update power system states."""
        for system_id, system in self.power_systems.items():
            # Update system condition
            if "condition" in system:
                # Power systems deteriorate over time
                deterioration_rate = 0.002 * time_delta  # 0.2% per hour
                system["condition"] = max(0.0, system["condition"] - deterioration_rate)

                # Check for critical condition
                if system["condition"] < 0.2:
                    self.logger.warning(
                        f"Power system {system['name']} is in critical condition"
                    )

    def _update_storage_facilities(self, time_delta: float):
        """Update storage facility states."""
        for facility_id, facility in self.storage_facilities.items():
            # Update facility condition
            if "condition" in facility:
                # Storage facilities deteriorate over time
                deterioration_rate = 0.001 * time_delta  # 0.1% per hour
                facility["condition"] = max(
                    0.0, facility["condition"] - deterioration_rate
                )

                # Check for critical condition
                if facility["condition"] < 0.2:
                    self.logger.warning(
                        f"Storage facility {facility['name']} is in critical condition"
                    )

    def get_state(self) -> Dict:
        """Get the current state of the infrastructure system."""
        return {
            "buildings": self.buildings,
            "roads": self.roads,
            "water_systems": self.water_systems,
            "power_systems": self.power_systems,
            "storage_facilities": self.storage_facilities,
        }

    def create_infrastructure(
        self,
        name: str,
        type: InfrastructureType,
        description: str,
        location: Tuple[float, float],
        capacity: float,
        properties: Dict[str, Any] = None,
        required_resources: Dict[str, float] = None,
    ) -> Infrastructure:
        """Create new infrastructure with custom properties."""
        if name in self.buildings:
            logger.warning(f"Infrastructure {name} already exists")
            return self.buildings[name]

        infrastructure = Infrastructure(
            name=name,
            type=type,
            description=description,
            location=location,
            capacity=capacity,
            properties=properties or {},
            required_resources=required_resources or {},
        )

        self.buildings[name] = infrastructure
        logger.info(f"Created new infrastructure: {name}")
        return infrastructure

    def create_structure(
        self,
        name: str,
        type: str,
        description: str,
        location: Tuple[float, float],
        size: float,
        capacity: int,
        properties: Dict[str, Any] = None,
        required_resources: Dict[str, float] = None,
    ) -> Structure:
        """Create new structure with custom type and properties."""
        if name in self.buildings:
            logger.warning(f"Structure {name} already exists")
            return self.buildings[name]

        structure = Structure(
            name=name,
            type=type,
            description=description,
            location=location,
            size=size,
            capacity=capacity,
            properties=properties or {},
            required_resources=required_resources or {},
        )

        self.buildings[name] = structure
        logger.info(f"Created new structure: {name} of type {type}")
        return structure

    def create_network(
        self, name: str, type: str, description: str, properties: Dict[str, Any] = None
    ) -> Network:
        """Create new network with custom type and properties."""
        if name in self.buildings:
            logger.warning(f"Network {name} already exists")
            return self.buildings[name]

        network = Network(
            name=name, type=type, description=description, properties=properties or {}
        )

        self.buildings[name] = network
        logger.info(f"Created new network: {name} of type {type}")
        return network

    def connect_infrastructure(self, network: str, infrastructure: str) -> bool:
        """Connect infrastructure to a network."""
        if network not in self.buildings:
            logger.error(f"Network {network} does not exist")
            return False

        if infrastructure not in self.buildings:
            logger.error(f"Infrastructure {infrastructure} does not exist")
            return False

        self.buildings[network].nodes.add(infrastructure)
        self.buildings[infrastructure].connected_to.add(network)

        logger.info(f"Connected {infrastructure} to {network}")
        return True

    def add_structure_occupant(self, structure: str, occupant: str) -> bool:
        """Add occupant to a structure."""
        if structure not in self.buildings:
            logger.error(f"Structure {structure} does not exist")
            return False

        if (
            len(self.buildings[structure].occupants)
            >= self.buildings[structure].capacity
        ):
            logger.error(f"Structure {structure} is at capacity")
            return False

        self.buildings[structure].occupants.add(occupant)
        logger.info(f"Added occupant {occupant} to {structure}")
        return True

    def remove_structure_occupant(self, structure: str, occupant: str) -> bool:
        """Remove occupant from a structure."""
        if structure not in self.buildings:
            logger.error(f"Structure {structure} does not exist")
            return False

        if occupant not in self.buildings[structure].occupants:
            logger.error(f"Occupant {occupant} is not in {structure}")
            return False

        self.buildings[structure].occupants.remove(occupant)
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
        for infrastructure in self.buildings.values():
            if isinstance(infrastructure, dict):
                level = infrastructure.get("maintenance", 1.0)
                infrastructure["maintenance"] = max(0.0, level - 0.001 * time_delta)
                infrastructure["age"] = infrastructure.get("age", 0.0) + time_delta
                if infrastructure["maintenance"] < 0.2:
                    self.logger.warning(
                        f"{infrastructure.get('name', 'Structure')} requires maintenance"
                    )
            else:
                infrastructure.maintenance = max(
                    0.0, infrastructure.maintenance - 0.001 * time_delta
                )
                infrastructure.age += time_delta
                if infrastructure.maintenance < 0.2:
                    self.logger.warning(f"{infrastructure.name} requires maintenance")

    def _update_network_efficiency(self, time_delta: float):
        """Update network efficiency based on emergent rules."""
        for network in self.buildings.values():
            target = None
            if isinstance(network, dict):
                if "efficiency" in network:
                    target = "dict"
            elif hasattr(network, "efficiency"):
                target = "obj"

            if target == "dict":
                change = random.uniform(-0.01, 0.01) * time_delta
                network["efficiency"] = min(
                    1.0, max(0.0, network["efficiency"] + change)
                )
            elif target == "obj":
                change = random.uniform(-0.01, 0.01) * time_delta
                network.efficiency = min(1.0, max(0.0, network.efficiency + change))

    def _update_structures(self, time_delta: float):
        """Update structure states based on emergent rules."""
        for structure in self.buildings.values():
            if isinstance(structure, dict):
                structure["age"] = structure.get("age", 0.0) + time_delta
            else:
                structure.age += time_delta

    def _check_infrastructure_events(self, time_delta: float):
        """Check for emergent infrastructure events."""
        for name, infra in self.buildings.items():
            level = infra.get(
                "maintenance", infra.maintenance if not isinstance(infra, dict) else 1.0
            )
            if level < 0.1:
                self.logger.error(f"Infrastructure {name} is failing")

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
                    "last_maintenance": infra.last_maintenance,
                }
                for name, infra in self.buildings.items()
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
                    "last_maintenance": structure.last_maintenance,
                }
                for name, structure in self.buildings.items()
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
                    "last_maintenance": network.last_maintenance,
                }
                for name, network in self.buildings.items()
            },
        }
