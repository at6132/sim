from typing import Dict

class AgentNeeds:
    def __init__(self):
        # Basic needs (0-1 scale, 0 = critical, 1 = satisfied)
        self.food = 1.0
        self.water = 1.0
        self.rest = 1.0
        self.shelter = 1.0
        
        # Social needs
        self.companionship = 1.0
        self.safety = 1.0
        self.belonging = 1.0
        
        # Advanced needs
        self.meaning = 1.0
        self.growth = 1.0
        self.contribution = 1.0
    
    def update(self, time_delta: float):
        """Update needs over time"""
        # Basic needs decay faster
        self.food = max(0.0, self.food - 0.01 * time_delta)
        self.water = max(0.0, self.water - 0.015 * time_delta)
        self.rest = max(0.0, self.rest - 0.005 * time_delta)
        self.shelter = max(0.0, self.shelter - 0.002 * time_delta)
        
        # Social needs decay slower
        self.companionship = max(0.0, self.companionship - 0.001 * time_delta)
        self.safety = max(0.0, self.safety - 0.001 * time_delta)
        self.belonging = max(0.0, self.belonging - 0.001 * time_delta)
        
        # Advanced needs decay very slowly
        self.meaning = max(0.0, self.meaning - 0.0005 * time_delta)
        self.growth = max(0.0, self.growth - 0.0005 * time_delta)
        self.contribution = max(0.0, self.contribution - 0.0005 * time_delta)
    
    def satisfy(self, need_type: str, amount: float):
        """Satisfy a specific need"""
        if hasattr(self, need_type):
            current_value = getattr(self, need_type)
            setattr(self, need_type, min(1.0, current_value + amount))
    
    def get_critical_needs(self) -> Dict[str, float]:
        """Get needs that are critically low (< 0.3)"""
        return {
            need: value for need, value in self.to_dict().items()
            if value < 0.3
        }
    
    def to_dict(self) -> Dict:
        """Convert needs to dictionary"""
        return {
            "food": self.food,
            "water": self.water,
            "rest": self.rest,
            "shelter": self.shelter,
            "companionship": self.companionship,
            "safety": self.safety,
            "belonging": self.belonging,
            "meaning": self.meaning,
            "growth": self.growth,
            "contribution": self.contribution
        } 