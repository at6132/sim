from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
import random
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Theory:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    evidence: List[str] = field(default_factory=list)
    predictions: List[str] = field(default_factory=list)
    acceptance: float = 0.0  # 0-1 scale
    complexity: float = 0.0  # 0-1 scale
    impact: float = 0.0  # 0-1 scale
    supporters: Set[str] = field(default_factory=set)  # Set of agent IDs
    critics: Set[str] = field(default_factory=set)  # Set of agent IDs
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Experiment:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    hypothesis: str = ""
    method: str = ""
    results: Dict[str, Any] = field(default_factory=dict)
    success_rate: float = 0.0  # 0-1 scale
    reproducibility: float = 0.0  # 0-1 scale
    impact: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Paradigm:
    name: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    core_principles: List[str] = field(default_factory=list)
    acceptance: float = 0.0  # 0-1 scale
    influence: float = 0.0  # 0-1 scale
    supporters: Set[str] = field(default_factory=set)  # Set of agent IDs
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class ScienceSystem:
    def __init__(self, world):
        """Initialize the science system."""
        self.world = world
        self.theories: Dict[str, Theory] = {}
        self.experiments: Dict[str, Experiment] = {}
        self.paradigms: Dict[str, Paradigm] = {}
        
    def create_theory(self, name: str, creator: str,
                     description: str = "") -> Theory:
        """Create a new scientific theory."""
        if name in self.theories:
            logger.warning(f"Theory {name} already exists")
            return self.theories[name]
            
        theory = Theory(
            name=name,
            creator=creator,
            description=description
        )
        
        self.theories[name] = theory
        logger.info(f"Created new theory: {name}")
        return theory
        
    def create_experiment(self, name: str, creator: str,
                         description: str = "", hypothesis: str = "") -> Experiment:
        """Create a new scientific experiment."""
        if name in self.experiments:
            logger.warning(f"Experiment {name} already exists")
            return self.experiments[name]
            
        experiment = Experiment(
            name=name,
            creator=creator,
            description=description,
            hypothesis=hypothesis
        )
        
        self.experiments[name] = experiment
        logger.info(f"Created new experiment: {name}")
        return experiment
        
    def create_paradigm(self, name: str, creator: str,
                       description: str = "") -> Paradigm:
        """Create a new scientific paradigm."""
        if name in self.paradigms:
            logger.warning(f"Paradigm {name} already exists")
            return self.paradigms[name]
            
        paradigm = Paradigm(
            name=name,
            creator=creator,
            description=description
        )
        
        self.paradigms[name] = paradigm
        logger.info(f"Created new paradigm: {name}")
        return paradigm
        
    def add_theory_supporter(self, theory: str, agent_id: str):
        """Add a supporter to a theory."""
        if theory in self.theories:
            self.theories[theory].supporters.add(agent_id)
            logger.info(f"Added supporter {agent_id} to theory {theory}")
            
    def remove_theory_supporter(self, theory: str, agent_id: str):
        """Remove a supporter from a theory."""
        if theory in self.theories:
            self.theories[theory].supporters.discard(agent_id)
            logger.info(f"Removed supporter {agent_id} from theory {theory}")
            
    def add_theory_critic(self, theory: str, agent_id: str):
        """Add a critic to a theory."""
        if theory in self.theories:
            self.theories[theory].critics.add(agent_id)
            logger.info(f"Added critic {agent_id} to theory {theory}")
            
    def remove_theory_critic(self, theory: str, agent_id: str):
        """Remove a critic from a theory."""
        if theory in self.theories:
            self.theories[theory].critics.discard(agent_id)
            logger.info(f"Removed critic {agent_id} from theory {theory}")
            
    def add_paradigm_supporter(self, paradigm: str, agent_id: str):
        """Add a supporter to a paradigm."""
        if paradigm in self.paradigms:
            self.paradigms[paradigm].supporters.add(agent_id)
            logger.info(f"Added supporter {agent_id} to paradigm {paradigm}")
            
    def remove_paradigm_supporter(self, paradigm: str, agent_id: str):
        """Remove a supporter from a paradigm."""
        if paradigm in self.paradigms:
            self.paradigms[paradigm].supporters.discard(agent_id)
            logger.info(f"Removed supporter {agent_id} from paradigm {paradigm}")
            
    def evolve_theory(self, name: str, time_delta: float):
        """Evolve a theory over time."""
        if name not in self.theories:
            return
            
        theory = self.theories[name]
        
        # Update acceptance based on supporters and critics
        supporter_factor = min(1.0, len(theory.supporters) / 100.0)
        critic_factor = min(1.0, len(theory.critics) / 100.0)
        theory.acceptance = (theory.acceptance * 0.9 + 
                           (supporter_factor - critic_factor) * 0.1)
                           
        # Update impact
        if len(theory.supporters) > 0:
            theory.impact = min(1.0,
                theory.impact + 0.01 * time_delta)
                
    def evolve_experiment(self, name: str, time_delta: float):
        """Evolve an experiment over time."""
        if name not in self.experiments:
            return
            
        experiment = self.experiments[name]
        
        # Update success rate
        if random.random() < 0.1 * time_delta:  # 10% chance per hour
            experiment.success_rate = min(1.0,
                experiment.success_rate + random.uniform(0.05, 0.1))
                
        # Update reproducibility
        if random.random() < 0.05 * time_delta:  # 5% chance per hour
            experiment.reproducibility = min(1.0,
                experiment.reproducibility + random.uniform(0.01, 0.05))
                
        # Update impact
        if experiment.success_rate > 0.5:
            experiment.impact = min(1.0,
                experiment.impact + 0.01 * time_delta)
                
    def evolve_paradigm(self, name: str, time_delta: float):
        """Evolve a paradigm over time."""
        if name not in self.paradigms:
            return
            
        paradigm = self.paradigms[name]
        
        # Update acceptance based on supporters
        supporter_factor = min(1.0, len(paradigm.supporters) / 100.0)
        paradigm.acceptance = (paradigm.acceptance * 0.9 + supporter_factor * 0.1)
        
        # Update influence
        if len(paradigm.supporters) > 0:
            paradigm.influence = min(1.0,
                paradigm.influence + 0.01 * time_delta)
                
    def check_paradigm_shift(self, time_delta: float):
        """Check for potential paradigm shifts."""
        for paradigm in self.paradigms.values():
            # Check if paradigm is losing support
            if (len(paradigm.supporters) < 10 and 
                random.random() < 0.01 * time_delta):  # 1% chance per hour
                self._trigger_paradigm_shift(paradigm)
                
    def _trigger_paradigm_shift(self, old_paradigm: Paradigm):
        """Trigger a paradigm shift from an old paradigm to a new one."""
        # Create new paradigm based on old one
        new_paradigm = Paradigm(
            name=f"New {old_paradigm.name}",
            creator="system",
            description=f"Evolution of {old_paradigm.name}",
            core_principles=old_paradigm.core_principles,
            acceptance=0.3,  # Start with lower acceptance
            influence=0.3
        )
        
        self.paradigms[new_paradigm.name] = new_paradigm
        logger.info(f"Paradigm shift: {old_paradigm.name} -> {new_paradigm.name}")
        
    def update(self, time_delta: float):
        """Update science system state."""
        # Evolve theories
        for name in list(self.theories.keys()):
            self.evolve_theory(name, time_delta)
            
        # Evolve experiments
        for name in list(self.experiments.keys()):
            self.evolve_experiment(name, time_delta)
            
        # Evolve paradigms
        for name in list(self.paradigms.keys()):
            self.evolve_paradigm(name, time_delta)
            
        # Check for paradigm shifts
        self.check_paradigm_shift(time_delta)
        
    def to_dict(self) -> Dict:
        """Convert science system state to dictionary for serialization."""
        return {
            "theories": {
                name: {
                    "name": theory.name,
                    "creator": theory.creator,
                    "creation_date": theory.creation_date,
                    "description": theory.description,
                    "evidence": theory.evidence,
                    "predictions": theory.predictions,
                    "acceptance": theory.acceptance,
                    "complexity": theory.complexity,
                    "impact": theory.impact,
                    "supporters": list(theory.supporters),
                    "critics": list(theory.critics),
                    "created_at": theory.created_at,
                    "last_update": theory.last_update
                }
                for name, theory in self.theories.items()
            },
            "experiments": {
                name: {
                    "name": experiment.name,
                    "creator": experiment.creator,
                    "creation_date": experiment.creation_date,
                    "description": experiment.description,
                    "hypothesis": experiment.hypothesis,
                    "method": experiment.method,
                    "results": experiment.results,
                    "success_rate": experiment.success_rate,
                    "reproducibility": experiment.reproducibility,
                    "impact": experiment.impact,
                    "created_at": experiment.created_at,
                    "last_update": experiment.last_update
                }
                for name, experiment in self.experiments.items()
            },
            "paradigms": {
                name: {
                    "name": paradigm.name,
                    "creator": paradigm.creator,
                    "creation_date": paradigm.creation_date,
                    "description": paradigm.description,
                    "core_principles": paradigm.core_principles,
                    "acceptance": paradigm.acceptance,
                    "influence": paradigm.influence,
                    "supporters": list(paradigm.supporters),
                    "created_at": paradigm.created_at,
                    "last_update": paradigm.last_update
                }
                for name, paradigm in self.paradigms.items()
            }
        } 