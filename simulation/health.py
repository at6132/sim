from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum
import random
from datetime import datetime
import time

class HealthStatus(Enum):
    HEALTHY = "healthy"
    SICK = "sick"
    INJURED = "injured"
    CRITICAL = "critical"
    DEAD = "dead"

@dataclass
class Disease:
    name: str
    severity: float  # 0.0 to 1.0
    contagious: bool
    symptoms: List[str]
    duration: float  # in hours
    treatment: Optional[str] = None
    resistance: float = 0.0  # 0.0 to 1.0

@dataclass
class Injury:
    name: str
    severity: float  # 0.0 to 1.0
    location: str
    healing_time: float  # in hours
    treatment: Optional[str] = None

class Health:
    def __init__(self):
        self.status = HealthStatus.HEALTHY
        self.diseases: List[Disease] = []
        self.injuries: List[Injury] = []
        self.immune_system: float = 1.0  # 0.0 to 1.0
        self.recovery_rate: float = 0.1  # Base recovery rate
        self.last_update = time.time()
        
    def update(self, time_delta: float) -> None:
        """Update health status over time."""
        # Update diseases
        for disease in self.diseases[:]:
            disease.duration -= time_delta
            if disease.duration <= 0:
                self.diseases.remove(disease)
                self.status = HealthStatus.HEALTHY
                
        # Update injuries
        for injury in self.injuries[:]:
            injury.healing_time -= time_delta
            if injury.healing_time <= 0:
                self.injuries.remove(injury)
                if not self.injuries:
                    self.status = HealthStatus.HEALTHY
                    
        # Update immune system
        if self.status == HealthStatus.HEALTHY:
            self.immune_system = min(1.0, self.immune_system + 0.01 * time_delta)
        else:
            self.immune_system = max(0.0, self.immune_system - 0.02 * time_delta)
            
        # Update status based on conditions
        if self.diseases or self.injuries:
            if any(d.severity > 0.7 for d in self.diseases) or any(i.severity > 0.7 for i in self.injuries):
                self.status = HealthStatus.CRITICAL
            else:
                self.status = HealthStatus.SICK if self.diseases else HealthStatus.INJURED
                
    def add_disease(self, disease: Disease) -> None:
        """Add a new disease."""
        self.diseases.append(disease)
        self.status = HealthStatus.SICK
        
    def add_injury(self, injury: Injury) -> None:
        """Add a new injury."""
        self.injuries.append(injury)
        self.status = HealthStatus.INJURED
        
    def treat_disease(self, disease_name: str, treatment: str) -> bool:
        """Attempt to treat a disease."""
        for disease in self.diseases:
            if disease.name == disease_name and disease.treatment == treatment:
                disease.duration *= 0.5  # Reduce duration
                return True
        return False
        
    def treat_injury(self, injury_name: str, treatment: str) -> bool:
        """Attempt to treat an injury."""
        for injury in self.injuries:
            if injury.name == injury_name and injury.treatment == treatment:
                injury.healing_time *= 0.5  # Reduce healing time
                return True
        return False
        
    def to_dict(self) -> Dict:
        """Convert health state to dictionary for serialization."""
        return {
            "status": self.status.value,
            "diseases": [
                {
                    "name": d.name,
                    "severity": d.severity,
                    "contagious": d.contagious,
                    "symptoms": d.symptoms,
                    "duration": d.duration,
                    "treatment": d.treatment,
                    "resistance": d.resistance
                }
                for d in self.diseases
            ],
            "injuries": [
                {
                    "name": i.name,
                    "severity": i.severity,
                    "location": i.location,
                    "healing_time": i.healing_time,
                    "treatment": i.treatment
                }
                for i in self.injuries
            ],
            "immune_system": self.immune_system,
            "recovery_rate": self.recovery_rate
        } 