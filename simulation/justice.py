from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
import random
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Law:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    punishment: str = ""
    enforcement_level: float = 0.0  # 0-1 scale
    acceptance: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Crime:
    name: str
    perpetrator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    laws_violated: List[str] = field(default_factory=list)  # List of law names
    severity: float = 0.0  # 0-1 scale
    evidence: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Trial:
    name: str
    crime: str  # Crime name
    creation_date: float = field(default_factory=time.time)
    judge: str  # Agent ID
    jury: List[str] = field(default_factory=list)  # List of agent IDs
    prosecutor: str  # Agent ID
    defender: str  # Agent ID
    verdict: Optional[str] = None
    sentence: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Prison:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    location: Tuple[float, float] = (0.0, 0.0)
    capacity: int = 0
    inmates: Set[str] = field(default_factory=set)  # Set of agent IDs
    security_level: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class JusticeSystem:
    def __init__(self, world):
        """Initialize the justice system."""
        self.world = world
        self.laws: Dict[str, Law] = {}
        self.crimes: Dict[str, Crime] = {}
        self.trials: Dict[str, Trial] = {}
        self.prisons: Dict[str, Prison] = {}
        
    def create_law(self, name: str, creator: str,
                  description: str = "", punishment: str = "") -> Law:
        """Create a new law."""
        if name in self.laws:
            logger.warning(f"Law {name} already exists")
            return self.laws[name]
            
        law = Law(
            name=name,
            creator=creator,
            description=description,
            punishment=punishment
        )
        
        self.laws[name] = law
        logger.info(f"Created new law: {name}")
        return law
        
    def create_crime(self, name: str, perpetrator: str,
                    description: str = "") -> Crime:
        """Create a new crime."""
        if name in self.crimes:
            logger.warning(f"Crime {name} already exists")
            return self.crimes[name]
            
        crime = Crime(
            name=name,
            perpetrator=perpetrator,
            description=description
        )
        
        self.crimes[name] = crime
        logger.info(f"Created new crime: {name}")
        return crime
        
    def create_trial(self, name: str, crime: str, judge: str,
                    prosecutor: str, defender: str) -> Trial:
        """Create a new trial."""
        if name in self.trials:
            logger.warning(f"Trial {name} already exists")
            return self.trials[name]
            
        trial = Trial(
            name=name,
            crime=crime,
            judge=judge,
            prosecutor=prosecutor,
            defender=defender
        )
        
        self.trials[name] = trial
        logger.info(f"Created new trial: {name}")
        return trial
        
    def create_prison(self, name: str, creator: str,
                     location: Tuple[float, float], capacity: int) -> Prison:
        """Create a new prison."""
        if name in self.prisons:
            logger.warning(f"Prison {name} already exists")
            return self.prisons[name]
            
        prison = Prison(
            name=name,
            creator=creator,
            location=location,
            capacity=capacity
        )
        
        self.prisons[name] = prison
        logger.info(f"Created new prison: {name}")
        return prison
        
    def add_jury_member(self, trial: str, agent_id: str):
        """Add a jury member to a trial."""
        if trial in self.trials:
            self.trials[trial].jury.append(agent_id)
            logger.info(f"Added jury member {agent_id} to trial {trial}")
            
    def add_inmate(self, prison: str, agent_id: str):
        """Add an inmate to a prison."""
        if prison in self.prisons:
            if len(self.prisons[prison].inmates) < self.prisons[prison].capacity:
                self.prisons[prison].inmates.add(agent_id)
                logger.info(f"Added inmate {agent_id} to prison {prison}")
            else:
                logger.warning(f"Prison {prison} is at capacity")
                
    def remove_inmate(self, prison: str, agent_id: str):
        """Remove an inmate from a prison."""
        if prison in self.prisons:
            self.prisons[prison].inmates.discard(agent_id)
            logger.info(f"Removed inmate {agent_id} from prison {prison}")
            
    def evolve_law(self, name: str, time_delta: float):
        """Evolve a law over time."""
        if name not in self.laws:
            return
            
        law = self.laws[name]
        
        # Update enforcement level
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            law.enforcement_level = min(1.0,
                law.enforcement_level + random.uniform(-0.1, 0.1))
                
        # Update acceptance
        if random.random() < 0.05 * time_delta:  # 5% chance per hour
            law.acceptance = min(1.0,
                law.acceptance + random.uniform(-0.05, 0.05))
                
    def evolve_crime(self, name: str, time_delta: float):
        """Evolve a crime over time."""
        if name not in self.crimes:
            return
            
        crime = self.crimes[name]
        
        # Update severity based on laws violated
        severity = 0.0
        for law_name in crime.laws_violated:
            if law_name in self.laws:
                law = self.laws[law_name]
                severity += law.enforcement_level
                
        if crime.laws_violated:
            severity /= len(crime.laws_violated)
            crime.severity = (crime.severity * 0.9 + severity * 0.1)
            
    def evolve_prison(self, name: str, time_delta: float):
        """Evolve a prison over time."""
        if name not in self.prisons:
            return
            
        prison = self.prisons[name]
        
        # Update security level based on capacity
        capacity_factor = len(prison.inmates) / prison.capacity
        prison.security_level = min(1.0,
            prison.security_level + (capacity_factor - 0.5) * 0.1 * time_delta)
            
    def update(self, time_delta: float):
        """Update justice system state."""
        # Evolve laws
        for name in list(self.laws.keys()):
            self.evolve_law(name, time_delta)
            
        # Evolve crimes
        for name in list(self.crimes.keys()):
            self.evolve_crime(name, time_delta)
            
        # Evolve prisons
        for name in list(self.prisons.keys()):
            self.evolve_prison(name, time_delta)
            
    def to_dict(self) -> Dict:
        """Convert justice system state to dictionary for serialization."""
        return {
            "laws": {
                name: {
                    "name": law.name,
                    "creator": law.creator,
                    "creation_date": law.creation_date,
                    "description": law.description,
                    "punishment": law.punishment,
                    "enforcement_level": law.enforcement_level,
                    "acceptance": law.acceptance,
                    "created_at": law.created_at,
                    "last_update": law.last_update
                }
                for name, law in self.laws.items()
            },
            "crimes": {
                name: {
                    "name": crime.name,
                    "perpetrator": crime.perpetrator,
                    "creation_date": crime.creation_date,
                    "description": crime.description,
                    "laws_violated": crime.laws_violated,
                    "severity": crime.severity,
                    "evidence": crime.evidence,
                    "created_at": crime.created_at,
                    "last_update": crime.last_update
                }
                for name, crime in self.crimes.items()
            },
            "trials": {
                name: {
                    "name": trial.name,
                    "crime": trial.crime,
                    "creation_date": trial.creation_date,
                    "judge": trial.judge,
                    "jury": trial.jury,
                    "prosecutor": trial.prosecutor,
                    "defender": trial.defender,
                    "verdict": trial.verdict,
                    "sentence": trial.sentence,
                    "created_at": trial.created_at,
                    "last_update": trial.last_update
                }
                for name, trial in self.trials.items()
            },
            "prisons": {
                name: {
                    "name": prison.name,
                    "creator": prison.creator,
                    "creation_date": prison.creation_date,
                    "location": prison.location,
                    "capacity": prison.capacity,
                    "inmates": list(prison.inmates),
                    "security_level": prison.security_level,
                    "created_at": prison.created_at,
                    "last_update": prison.last_update
                }
                for name, prison in self.prisons.items()
            }
        } 