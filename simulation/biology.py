from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random
import uuid
from datetime import datetime, timedelta

@dataclass
class Pregnancy:
    mother_id: str
    father_id: str
    conception_time: datetime
    due_date: datetime
    gestation_period: int = 280  # days

@dataclass
class Child:
    id: str
    mother_id: str
    father_id: str
    birth_time: datetime
    genes: Dict[str, float]
    name: str

class Biology:
    def __init__(self):
        self.pregnancies: List[Pregnancy] = []
        self.children: List[Child] = []
        self.mating_cooldowns: Dict[str, datetime] = {}  # agent_id -> last mating time

    def can_mate(self, agent1_id: str, agent2_id: str) -> bool:
        """Check if two agents can mate."""
        current_time = datetime.now()
        
        # Check mating cooldowns
        if (agent1_id in self.mating_cooldowns and 
            current_time - self.mating_cooldowns[agent1_id] < timedelta(days=365)):
            return False
        if (agent2_id in self.mating_cooldowns and 
            current_time - self.mating_cooldowns[agent2_id] < timedelta(days=365)):
            return False
            
        return True

    def initiate_pregnancy(self, mother_id: str, father_id: str) -> Optional[Pregnancy]:
        """Start a new pregnancy if conditions are met."""
        if not self.can_mate(mother_id, father_id):
            return None

        current_time = datetime.now()
        pregnancy = Pregnancy(
            mother_id=mother_id,
            father_id=father_id,
            conception_time=current_time,
            due_date=current_time + timedelta(days=280)
        )
        
        self.pregnancies.append(pregnancy)
        self.mating_cooldowns[mother_id] = current_time
        self.mating_cooldowns[father_id] = current_time
        
        return pregnancy

    def check_pregnancies(self, current_time: datetime) -> List[Child]:
        """Check for pregnancies that have reached term."""
        new_children = []
        remaining_pregnancies = []
        
        for pregnancy in self.pregnancies:
            if current_time >= pregnancy.due_date:
                # Create new child with inherited genes
                child = self._create_child(pregnancy, current_time)
                new_children.append(child)
            else:
                remaining_pregnancies.append(pregnancy)
                
        self.pregnancies = remaining_pregnancies
        return new_children

    def _create_child(self, pregnancy: Pregnancy, birth_time: datetime) -> Child:
        """Create a new child with inherited genes."""
        # Generate a unique ID for the child
        child_id = str(uuid.uuid4())
        
        # Create a name based on birth order
        child_number = len(self.children) + 1
        name = f"Child{child_number}"
        
        # Inherit and mutate genes
        # This would be expanded based on the actual gene structure
        genes = {
            "curiosity": random.uniform(0.0, 1.0),
            "strength": random.uniform(0.0, 1.0),
            "intelligence": random.uniform(0.0, 1.0),
            "social_drive": random.uniform(0.0, 1.0),
            "creativity": random.uniform(0.0, 1.0),
            "adaptability": random.uniform(0.0, 1.0)
        }
        
        child = Child(
            id=child_id,
            mother_id=pregnancy.mother_id,
            father_id=pregnancy.father_id,
            birth_time=birth_time,
            genes=genes,
            name=name
        )
        
        self.children.append(child)
        return child

    def get_pregnancy_status(self, agent_id: str) -> Optional[Pregnancy]:
        """Get pregnancy status for an agent."""
        for pregnancy in self.pregnancies:
            if pregnancy.mother_id == agent_id:
                return pregnancy
        return None

    def get_children(self, agent_id: str) -> List[Child]:
        """Get all children of an agent."""
        return [
            child for child in self.children
            if child.mother_id == agent_id or child.father_id == agent_id
        ]

    def to_dict(self) -> Dict:
        """Convert biology state to dictionary for serialization."""
        return {
            'pregnancies': [
                {
                    'mother_id': p.mother_id,
                    'father_id': p.father_id,
                    'conception_time': p.conception_time.isoformat(),
                    'due_date': p.due_date.isoformat()
                }
                for p in self.pregnancies
            ],
            'children': [
                {
                    'id': c.id,
                    'mother_id': c.mother_id,
                    'father_id': c.father_id,
                    'birth_time': c.birth_time.isoformat(),
                    'genes': c.genes,
                    'name': c.name
                }
                for c in self.children
            ],
            'mating_cooldowns': {
                agent_id: time.isoformat()
                for agent_id, time in self.mating_cooldowns.items()
            }
        } 