from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum
import random
from datetime import datetime
import time

class ResourceType(Enum):
    FOOD = "food"
    WATER = "water"
    WOOD = "wood"
    STONE = "stone"
    METAL = "metal"
    CLOTH = "cloth"
    TOOLS = "tools"
    WEAPONS = "weapons"
    SHELTER = "shelter"
    MEDICINE = "medicine"

class TradeType(Enum):
    BARTER = "barter"
    CURRENCY = "currency"
    GIFT = "gift"
    TRIBUTE = "tribute"

@dataclass
class Resource:
    type: ResourceType
    amount: float
    quality: float  # 0.0 to 1.0
    source: str
    production_time: float  # in hours
    value: float  # base value

@dataclass
class Trade:
    type: TradeType
    resources_given: Dict[ResourceType, float]
    resources_received: Dict[ResourceType, float]
    partner_id: str
    timestamp: float
    success: bool
    value_ratio: float  # value received / value given

class Economy:
    def __init__(self):
        self.resources: Dict[ResourceType, Resource] = {}
        self.trade_history: List[Trade] = []
        self.wealth: float = 0.0
        self.production_capacity: Dict[ResourceType, float] = {}
        self.last_update = time.time()
        
    def update(self, time_delta: float) -> None:
        """Update economic state over time."""
        # Update resource production
        for resource_type, capacity in self.production_capacity.items():
            if resource_type in self.resources:
                resource = self.resources[resource_type]
                production = capacity * time_delta
                resource.amount += production
                
        # Update resource values based on scarcity
        total_resources = sum(r.amount for r in self.resources.values())
        for resource in self.resources.values():
            if total_resources > 0:
                scarcity = 1.0 - (resource.amount / total_resources)
                resource.value *= (1.0 + scarcity * 0.1)  # Increase value based on scarcity
                
    def add_resource(self, resource: Resource) -> None:
        """Add a new resource."""
        if resource.type in self.resources:
            existing = self.resources[resource.type]
            # Combine resources, weighted by quality
            total_amount = existing.amount + resource.amount
            existing.quality = (existing.quality * existing.amount + 
                              resource.quality * resource.amount) / total_amount
            existing.amount = total_amount
        else:
            self.resources[resource.type] = resource
            
    def remove_resource(self, resource_type: ResourceType, amount: float) -> bool:
        """Remove resources if available."""
        if resource_type in self.resources:
            resource = self.resources[resource_type]
            if resource.amount >= amount:
                resource.amount -= amount
                return True
        return False
        
    def calculate_trade_value(self, resources: Dict[ResourceType, float]) -> float:
        """Calculate the total value of a set of resources."""
        return sum(
            self.resources.get(r_type, Resource(r_type, 0, 0.5, "unknown", 0, 1.0)).value * amount
            for r_type, amount in resources.items()
        )
        
    def propose_trade(self, partner_id: str, give: Dict[ResourceType, float], 
                     receive: Dict[ResourceType, float], trade_type: TradeType) -> Optional[Trade]:
        """Propose a trade with another agent."""
        # Check if we have enough resources
        for resource_type, amount in give.items():
            if not self.remove_resource(resource_type, amount):
                return None
                
        # Calculate value ratio
        given_value = self.calculate_trade_value(give)
        received_value = self.calculate_trade_value(receive)
        value_ratio = received_value / given_value if given_value > 0 else 0
        
        # Create trade record
        trade = Trade(
            type=trade_type,
            resources_given=give,
            resources_received=receive,
            partner_id=partner_id,
            timestamp=time.time(),
            success=True,
            value_ratio=value_ratio
        )
        
        self.trade_history.append(trade)
        self.wealth += received_value - given_value
        
        return trade
        
    def get_resource_amount(self, resource_type: ResourceType) -> float:
        """Get the current amount of a resource."""
        return self.resources.get(resource_type, Resource(resource_type, 0, 0.5, "unknown", 0, 1.0)).amount
        
    def get_resource_quality(self, resource_type: ResourceType) -> float:
        """Get the current quality of a resource."""
        return self.resources.get(resource_type, Resource(resource_type, 0, 0.5, "unknown", 0, 1.0)).quality
        
    def to_dict(self) -> Dict:
        """Convert economic state to dictionary for serialization."""
        return {
            "resources": {
                r_type.value: {
                    "amount": r.amount,
                    "quality": r.quality,
                    "source": r.source,
                    "production_time": r.production_time,
                    "value": r.value
                }
                for r_type, r in self.resources.items()
            },
            "trade_history": [
                {
                    "type": t.type.value,
                    "resources_given": {r.value: a for r, a in t.resources_given.items()},
                    "resources_received": {r.value: a for r, a in t.resources_received.items()},
                    "partner_id": t.partner_id,
                    "timestamp": t.timestamp,
                    "success": t.success,
                    "value_ratio": t.value_ratio
                }
                for t in self.trade_history
            ],
            "wealth": self.wealth,
            "production_capacity": {
                r_type.value: capacity
                for r_type, capacity in self.production_capacity.items()
            }
        } 