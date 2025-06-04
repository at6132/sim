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
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    target_audience: Set[str] = field(default_factory=set)  # Set of agent IDs
    reach: float = 0.0  # 0-1 scale
    believability: float = 0.0  # 0-1 scale
    emotional_impact: float = 0.0  # 0-1 scale
    spread_rate: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Campaign:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    messages: List[str] = field(default_factory=list)  # List of message IDs
    target_audience: Set[str] = field(default_factory=set)  # Set of agent IDs
    success_rate: float = 0.0  # 0-1 scale
    influence: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class PropagandaSystem:
    def __init__(self, world):
        """Initialize the propaganda system."""
        self.world = world
        self.messages: Dict[str, Message] = {}
        self.campaigns: Dict[str, Campaign] = {}
        
    def create_message(self, content: str, creator: str,
                      target_audience: Optional[Set[str]] = None) -> Message:
        """Create a new propaganda message."""
        message = Message(
            content=content,
            creator=creator,
            target_audience=target_audience or set()
        )
        
        message_id = f"msg_{len(self.messages)}"
        self.messages[message_id] = message
        logger.info(f"Created new message: {message_id}")
        return message
        
    def create_campaign(self, name: str, creator: str,
                       description: str = "") -> Campaign:
        """Create a new propaganda campaign."""
        if name in self.campaigns:
            logger.warning(f"Campaign {name} already exists")
            return self.campaigns[name]
            
        campaign = Campaign(
            name=name,
            creator=creator,
            description=description
        )
        
        self.campaigns[name] = campaign
        logger.info(f"Created new campaign: {name}")
        return campaign
        
    def add_message_to_campaign(self, campaign: str, message_id: str):
        """Add a message to a campaign."""
        if campaign in self.campaigns and message_id in self.messages:
            self.campaigns[campaign].messages.append(message_id)
            logger.info(f"Added message {message_id} to campaign {campaign}")
            
    def add_target_to_campaign(self, campaign: str, agent_id: str):
        """Add a target audience member to a campaign."""
        if campaign in self.campaigns:
            self.campaigns[campaign].target_audience.add(agent_id)
            logger.info(f"Added target {agent_id} to campaign {campaign}")
            
    def evolve_message(self, message_id: str, time_delta: float):
        """Evolve a message over time."""
        if message_id not in self.messages:
            return
            
        message = self.messages[message_id]
        
        # Update reach based on audience size
        audience_factor = min(1.0, len(message.target_audience) / 100.0)
        message.reach = (message.reach * 0.9 + audience_factor * 0.1)
        
        # Update believability
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            message.believability = min(1.0,
                message.believability + random.uniform(-0.1, 0.1))
                
        # Update emotional impact
        if random.random() < 0.05 * time_delta:  # 5% chance per hour
            message.emotional_impact = min(1.0,
                message.emotional_impact + random.uniform(-0.05, 0.05))
                
        # Update spread rate
        message.spread_rate = (
            message.believability * 0.4 +
            message.emotional_impact * 0.4 +
            message.reach * 0.2
        )
        
    def evolve_campaign(self, name: str, time_delta: float):
        """Evolve a campaign over time."""
        if name not in self.campaigns:
            return
            
        campaign = self.campaigns[name]
        
        # Update success rate based on message performance
        message_success = 0.0
        for message_id in campaign.messages:
            if message_id in self.messages:
                message = self.messages[message_id]
                message_success += (
                    message.believability * 0.4 +
                    message.emotional_impact * 0.4 +
                    message.reach * 0.2
                )
                
        if campaign.messages:
            message_success /= len(campaign.messages)
            campaign.success_rate = (campaign.success_rate * 0.9 + message_success * 0.1)
            
        # Update influence
        audience_factor = min(1.0, len(campaign.target_audience) / 100.0)
        campaign.influence = (campaign.influence * 0.9 + 
                            (audience_factor * campaign.success_rate) * 0.1)
                            
    def update(self, time_delta: float):
        """Update propaganda system state."""
        # Evolve messages
        for message_id in list(self.messages.keys()):
            self.evolve_message(message_id, time_delta)
            
        # Evolve campaigns
        for name in list(self.campaigns.keys()):
            self.evolve_campaign(name, time_delta)
            
    def to_dict(self) -> Dict:
        """Convert propaganda system state to dictionary for serialization."""
        return {
            "messages": {
                message_id: {
                    "content": message.content,
                    "creator": message.creator,
                    "creation_date": message.creation_date,
                    "target_audience": list(message.target_audience),
                    "reach": message.reach,
                    "believability": message.believability,
                    "emotional_impact": message.emotional_impact,
                    "spread_rate": message.spread_rate,
                    "created_at": message.created_at,
                    "last_update": message.last_update
                }
                for message_id, message in self.messages.items()
            },
            "campaigns": {
                name: {
                    "name": campaign.name,
                    "creator": campaign.creator,
                    "creation_date": campaign.creation_date,
                    "description": campaign.description,
                    "messages": campaign.messages,
                    "target_audience": list(campaign.target_audience),
                    "success_rate": campaign.success_rate,
                    "influence": campaign.influence,
                    "created_at": campaign.created_at,
                    "last_update": campaign.last_update
                }
                for name, campaign in self.campaigns.items()
            }
        } 