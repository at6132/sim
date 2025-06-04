from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
import random
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Message:
    content: str
    sender: str  # Agent ID
    recipient: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    delivery_time: Optional[float] = None
    status: str = "pending"  # pending, delivered, failed
    priority: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class CommunicationMethod:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    type: str = ""  # Let agents define types
    range: float = 0.0  # Maximum distance in units
    speed: float = 0.0  # Units per hour
    reliability: float = 1.0  # 0-1 scale
    cost: float = 0.0  # Resource cost per message
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Network:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    nodes: List[Tuple[float, float]] = field(default_factory=list)  # Network node locations
    connections: List[Tuple[int, int]] = field(default_factory=list)  # Indices of connected nodes
    method: str  # Communication method name
    coverage: float = 0.0  # 0-1 scale
    efficiency: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class CommunicationSystem:
    def __init__(self, world):
        """Initialize the communication system."""
        self.world = world
        self.messages: Dict[str, Message] = {}
        self.methods: Dict[str, CommunicationMethod] = {}
        self.networks: Dict[str, Network] = {}
        
    def create_message(self, content: str, sender: str,
                      recipient: str, priority: float = 0.0) -> Message:
        """Create a new message."""
        message = Message(
            content=content,
            sender=sender,
            recipient=recipient,
            priority=priority
        )
        
        message_id = f"msg_{len(self.messages)}"
        self.messages[message_id] = message
        logger.info(f"Created new message: {message_id}")
        return message
        
    def create_communication_method(self, name: str, creator: str,
                                  type: str, range: float,
                                  speed: float, cost: float) -> CommunicationMethod:
        """Create a new communication method."""
        if name in self.methods:
            logger.warning(f"Communication method {name} already exists")
            return self.methods[name]
            
        method = CommunicationMethod(
            name=name,
            creator=creator,
            type=type,
            range=range,
            speed=speed,
            cost=cost
        )
        
        self.methods[name] = method
        logger.info(f"Created new communication method: {name}")
        return method
        
    def create_network(self, name: str, creator: str,
                      nodes: List[Tuple[float, float]],
                      connections: List[Tuple[int, int]],
                      method: str) -> Network:
        """Create a new communication network."""
        if name in self.networks:
            logger.warning(f"Network {name} already exists")
            return self.networks[name]
            
        network = Network(
            name=name,
            creator=creator,
            nodes=nodes,
            connections=connections,
            method=method
        )
        
        self.networks[name] = network
        logger.info(f"Created new network: {name}")
        return network
        
    def send_message(self, message_id: str, method: str):
        """Send a message using a communication method."""
        if message_id not in self.messages or method not in self.methods:
            return
            
        message = self.messages[message_id]
        comm_method = self.methods[method]
        
        # Calculate delivery time based on distance and speed
        sender_pos = self.world.get_agent_position(message.sender)
        recipient_pos = self.world.get_agent_position(message.recipient)
        
        if sender_pos and recipient_pos:
            distance = ((recipient_pos[0] - sender_pos[0])**2 +
                       (recipient_pos[1] - sender_pos[1])**2)**0.5
                       
            if distance <= comm_method.range:
                message.delivery_time = time.time() + (distance / comm_method.speed)
                message.status = "delivered"
                logger.info(f"Message {message_id} sent via {method}")
            else:
                message.status = "failed"
                logger.warning(f"Message {message_id} failed: out of range")
                
    def evolve_method(self, name: str, time_delta: float):
        """Evolve a communication method over time."""
        if name not in self.methods:
            return
            
        method = self.methods[name]
        
        # Update reliability based on random events
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            method.reliability = max(0.0,
                method.reliability - random.uniform(0.0, 0.1))
                
    def evolve_network(self, name: str, time_delta: float):
        """Evolve a network over time."""
        if name not in self.networks:
            return
            
        network = self.networks[name]
        
        # Update coverage based on nodes and connections
        if network.nodes and network.connections:
            node_density = len(network.connections) / len(network.nodes)
            network.coverage = min(1.0, node_density / 2.0)
            
        # Update efficiency based on method reliability
        if network.method in self.methods:
            method = self.methods[network.method]
            network.efficiency = network.coverage * method.reliability
            
    def update(self, time_delta: float):
        """Update communication system state."""
        # Process pending messages
        current_time = time.time()
        for message_id, message in self.messages.items():
            if message.status == "pending" and message.delivery_time:
                if current_time >= message.delivery_time:
                    message.status = "delivered"
                    logger.info(f"Message {message_id} delivered")
                    
        # Evolve methods
        for name in list(self.methods.keys()):
            self.evolve_method(name, time_delta)
            
        # Evolve networks
        for name in list(self.networks.keys()):
            self.evolve_network(name, time_delta)
            
    def to_dict(self) -> Dict:
        """Convert communication system state to dictionary for serialization."""
        return {
            "messages": {
                message_id: {
                    "content": message.content,
                    "sender": message.sender,
                    "recipient": message.recipient,
                    "creation_date": message.creation_date,
                    "delivery_time": message.delivery_time,
                    "status": message.status,
                    "priority": message.priority,
                    "created_at": message.created_at,
                    "last_update": message.last_update
                }
                for message_id, message in self.messages.items()
            },
            "methods": {
                name: {
                    "name": method.name,
                    "creator": method.creator,
                    "creation_date": method.creation_date,
                    "type": method.type,
                    "range": method.range,
                    "speed": method.speed,
                    "reliability": method.reliability,
                    "cost": method.cost,
                    "created_at": method.created_at,
                    "last_update": method.last_update
                }
                for name, method in self.methods.items()
            },
            "networks": {
                name: {
                    "name": network.name,
                    "creator": network.creator,
                    "creation_date": network.creation_date,
                    "nodes": network.nodes,
                    "connections": network.connections,
                    "method": network.method,
                    "coverage": network.coverage,
                    "efficiency": network.efficiency,
                    "created_at": network.created_at,
                    "last_update": network.last_update
                }
                for name, network in self.networks.items()
            }
        } 