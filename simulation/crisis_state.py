from dataclasses import dataclass
from typing import Dict, List
import random

@dataclass
class CrisisState:
    # Crisis levels
    physical_crisis: float = 0.0  # Physical health crisis (0-1)
    mental_crisis: float = 0.0    # Mental health crisis (0-1)
    social_crisis: float = 0.0    # Social relationship crisis (0-1)
    existential_crisis: float = 0.0  # Existential crisis (0-1)
    
    # Crisis triggers
    triggers: Dict[str, float] = None  # Events that trigger crises
    coping_mechanisms: Dict[str, float] = None  # Ways of coping with crises
    
    # Crisis history
    crisis_history: List[Dict] = None  # History of past crises
    
    def __init__(self):
        """Initialize crisis state with empty values."""
        self.physical_crisis = 0.0
        self.mental_crisis = 0.0
        self.social_crisis = 0.0
        self.existential_crisis = 0.0
        self.triggers = {}
        self.coping_mechanisms = {}
        self.crisis_history = []
        
    def update(self, time_delta: float, world_state: Dict):
        """Update crisis state over time based on world state."""
        # Update crisis levels based on triggers
        if "physical_damage" in world_state:
            self.physical_crisis = min(1.0, self.physical_crisis + world_state["physical_damage"] * 0.1)
        if "mental_stress" in world_state:
            self.mental_crisis = min(1.0, self.mental_crisis + world_state["mental_stress"] * 0.1)
        if "social_conflict" in world_state:
            self.social_crisis = min(1.0, self.social_crisis + world_state["social_conflict"] * 0.1)
        if "existential_doubt" in world_state:
            self.existential_crisis = min(1.0, self.existential_crisis + world_state["existential_doubt"] * 0.1)
            
        # Natural recovery from crises
        self.physical_crisis = max(0.0, self.physical_crisis - time_delta * 0.0001)
        self.mental_crisis = max(0.0, self.mental_crisis - time_delta * 0.0001)
        self.social_crisis = max(0.0, self.social_crisis - time_delta * 0.0001)
        self.existential_crisis = max(0.0, self.existential_crisis - time_delta * 0.0001)
        
        # Record significant crises
        self._record_crises()
        
    def _record_crises(self):
        """Record significant crises in history."""
        current_crises = {
            "physical": self.physical_crisis,
            "mental": self.mental_crisis,
            "social": self.social_crisis,
            "existential": self.existential_crisis
        }
        
        # Record if any crisis is significant
        if any(level > 0.7 for level in current_crises.values()):
            self.crisis_history.append({
                "timestamp": time.time(),
                "crises": current_crises,
                "triggers": self.triggers.copy()
            })
            
    def add_trigger(self, trigger: str, severity: float):
        """Add a crisis trigger."""
        self.triggers[trigger] = severity
        
    def add_coping_mechanism(self, mechanism: str, effectiveness: float):
        """Add a coping mechanism."""
        self.coping_mechanisms[mechanism] = effectiveness
        
    def get_total_crisis_level(self) -> float:
        """Get the total crisis level."""
        return max(
            self.physical_crisis,
            self.mental_crisis,
            self.social_crisis,
            self.existential_crisis
        )
        
    def is_in_crisis(self) -> bool:
        """Check if agent is in any significant crisis."""
        return self.get_total_crisis_level() > 0.7
        
    def to_dict(self) -> Dict:
        """Convert crisis state to dictionary for saving."""
        return {
            "physical_crisis": self.physical_crisis,
            "mental_crisis": self.mental_crisis,
            "social_crisis": self.social_crisis,
            "existential_crisis": self.existential_crisis,
            "triggers": self.triggers,
            "coping_mechanisms": self.coping_mechanisms,
            "crisis_history": self.crisis_history
        }
        
    def update_from_dict(self, data: Dict):
        """Update crisis state from saved data."""
        self.physical_crisis = data.get("physical_crisis", self.physical_crisis)
        self.mental_crisis = data.get("mental_crisis", self.mental_crisis)
        self.social_crisis = data.get("social_crisis", self.social_crisis)
        self.existential_crisis = data.get("existential_crisis", self.existential_crisis)
        self.triggers = data.get("triggers", self.triggers)
        self.coping_mechanisms = data.get("coping_mechanisms", self.coping_mechanisms)
        self.crisis_history = data.get("crisis_history", self.crisis_history) 