from dataclasses import dataclass
from typing import Dict, List, Set
import random

@dataclass
class SocialState:
    # Social status
    status: str = "commoner"  # Current social status
    reputation: float = 0.5  # Overall reputation (0-1)
    influence: float = 0.5  # Social influence (0-1)
    
    # Relationships
    friends: Set[str] = None  # Set of friend IDs
    enemies: Set[str] = None  # Set of enemy IDs
    allies: Set[str] = None  # Set of ally IDs
    
    # Social roles
    roles: List[str] = None  # Current social roles
    responsibilities: Dict[str, float] = None  # Role responsibilities
    
    # Social skills
    leadership: float = 0.5  # Leadership ability (0-1)
    diplomacy: float = 0.5  # Diplomatic ability (0-1)
    charisma: float = 0.5  # Charismatic ability (0-1)
    
    def __init__(self):
        """Initialize social state with basic values."""
        self.status = "commoner"
        self.reputation = 0.5
        self.influence = 0.5
        self.friends = set()
        self.enemies = set()
        self.allies = set()
        self.roles = []
        self.responsibilities = {}
        self.leadership = 0.5
        self.diplomacy = 0.5
        self.charisma = 0.5
        
    def update(self, time_delta: float, world_state: Dict):
        """Update social state over time based on world state."""
        # Update reputation based on actions
        if "good_deed" in world_state:
            self.reputation = min(1.0, self.reputation + world_state["good_deed"] * 0.1)
        if "bad_deed" in world_state:
            self.reputation = max(0.0, self.reputation - world_state["bad_deed"] * 0.1)
            
        # Update influence based on status and reputation
        self.influence = (self.reputation + self._get_status_value()) / 2
        
        # Update social skills
        self._update_skills(time_delta)
        
    def _get_status_value(self) -> float:
        """Get numeric value for current status."""
        status_values = {
            "commoner": 0.3,
            "merchant": 0.4,
            "artisan": 0.5,
            "scholar": 0.6,
            "noble": 0.7,
            "royalty": 0.9
        }
        return status_values.get(self.status, 0.3)
        
    def _update_skills(self, time_delta: float):
        """Update social skills over time."""
        # Skills improve with use
        if len(self.roles) > 0:
            self.leadership = min(1.0, self.leadership + time_delta * 0.0001)
        if len(self.friends) > 0:
            self.diplomacy = min(1.0, self.diplomacy + time_delta * 0.0001)
        if self.influence > 0.5:
            self.charisma = min(1.0, self.charisma + time_delta * 0.0001)
            
    def add_friend(self, agent_id: str):
        """Add a friend."""
        self.friends.add(agent_id)
        if agent_id in self.enemies:
            self.enemies.remove(agent_id)
            
    def add_enemy(self, agent_id: str):
        """Add an enemy."""
        self.enemies.add(agent_id)
        if agent_id in self.friends:
            self.friends.remove(agent_id)
            
    def add_ally(self, agent_id: str):
        """Add an ally."""
        self.allies.add(agent_id)
        
    def add_role(self, role: str, responsibility: float = 0.5):
        """Add a social role with responsibility level."""
        if role not in self.roles:
            self.roles.append(role)
        self.responsibilities[role] = responsibility
        
    def remove_role(self, role: str):
        """Remove a social role."""
        if role in self.roles:
            self.roles.remove(role)
        if role in self.responsibilities:
            del self.responsibilities[role]
            
    def to_dict(self) -> Dict:
        """Convert social state to dictionary for saving."""
        return {
            "status": self.status,
            "reputation": self.reputation,
            "influence": self.influence,
            "friends": list(self.friends),
            "enemies": list(self.enemies),
            "allies": list(self.allies),
            "roles": self.roles,
            "responsibilities": self.responsibilities,
            "leadership": self.leadership,
            "diplomacy": self.diplomacy,
            "charisma": self.charisma
        }
        
    def update_from_dict(self, data: Dict):
        """Update social state from saved data."""
        self.status = data.get("status", self.status)
        self.reputation = data.get("reputation", self.reputation)
        self.influence = data.get("influence", self.influence)
        self.friends = set(data.get("friends", []))
        self.enemies = set(data.get("enemies", []))
        self.allies = set(data.get("allies", []))
        self.roles = data.get("roles", self.roles)
        self.responsibilities = data.get("responsibilities", self.responsibilities)
        self.leadership = data.get("leadership", self.leadership)
        self.diplomacy = data.get("diplomacy", self.diplomacy)
        self.charisma = data.get("charisma", self.charisma) 