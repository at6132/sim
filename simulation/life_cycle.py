from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
from datetime import datetime, timedelta
import time

class LifeStage(Enum):
    INFANT = "infant"  # 0-2 years
    CHILD = "child"    # 2-12 years
    ADOLESCENT = "adolescent"  # 12-18 years
    ADULT = "adult"    # 18-50 years
    ELDER = "elder"    # 50+ years

class PregnancyStage(Enum):
    FIRST_TRIMESTER = "first_trimester"  # 0-3 months
    SECOND_TRIMESTER = "second_trimester"  # 3-6 months
    THIRD_TRIMESTER = "third_trimester"  # 6-9 months

@dataclass
class Pregnancy:
    start_date: datetime
    father_id: str
    stage: PregnancyStage = PregnancyStage.FIRST_TRIMESTER
    health: float = 1.0
    complications: List[str] = field(default_factory=list)
    nutrition_level: float = 1.0
    stress_level: float = 0.0

@dataclass
class Resource:
    type: str
    amount: float
    quality: float
    location: Tuple[int, int]
    last_harvested: Optional[datetime] = None
    regrowth_rate: float = 0.1  # Amount regenerated per day

@dataclass
class CourtshipState:
    is_courting: bool = False
    courtship_target: Optional[str] = None
    courtship_progress: float = 0.0  # 0-100
    courtship_actions: List[str] = field(default_factory=list)
    last_courtship_time: float = 0.0
    courtship_cooldown: float = 0.0

@dataclass
class FamilyRelationship:
    relationship_type: str  # parent, child, sibling, mate
    related_agent_id: str
    bond_strength: float = 0.0  # 0-100
    last_interaction_time: float = 0.0
    shared_memories: List[Dict] = field(default_factory=list)

@dataclass
class LifeCycleSystem:
    def __init__(self):
        self.pregnancies: Dict[str, Pregnancy] = {}  # agent_id -> pregnancy
        self.resources: Dict[str, List[Resource]] = {}  # resource_type -> resources
        self.death_records: List[Dict] = []
        self.birth_records: List[Dict] = []
        self.courtships: Dict[str, CourtshipState] = {}
        self.family_relationships: Dict[str, List[FamilyRelationship]] = {}
        
    def update_agent(self, agent: 'Agent', time_delta: float, world_state: Dict):
        """Update agent's life cycle state."""
        # Update age and life stage
        self._update_age(agent, time_delta)
        
        # Update pregnancy if applicable
        if agent.id in self.pregnancies:
            self._update_pregnancy(agent, time_delta)
            
        # Update resource gathering
        self._update_resources(agent, time_delta, world_state)
        
        # Check for death
        if self._should_die(agent):
            self._handle_death(agent)
            
        # Check for reproduction
        if self._can_reproduce(agent):
            self._attempt_reproduction(agent, world_state)
            
    def _update_age(self, agent: 'Agent', time_delta: float):
        """Update agent's age and life stage."""
        # Convert time_delta to years
        years_passed = time_delta / 365.0
        agent.age += years_passed
        
        # Update life stage
        if agent.age < 2:
            agent.life_stage = LifeStage.INFANT
        elif agent.age < 12:
            agent.life_stage = LifeStage.CHILD
        elif agent.age < 18:
            agent.life_stage = LifeStage.ADOLESCENT
        elif agent.age < 50:
            agent.life_stage = LifeStage.ADULT
        else:
            agent.life_stage = LifeStage.ELDER
            
        # Update health based on age
        if agent.life_stage == LifeStage.ELDER:
            agent.health *= 0.999  # Gradual health decline in old age
            
    def _update_pregnancy(self, agent: 'Agent', time_delta: float):
        """Update pregnancy state."""
        pregnancy = self.pregnancies[agent.id]
        
        # Update pregnancy stage
        days_pregnant = (datetime.now() - pregnancy.start_date).days
        if days_pregnant < 90:
            pregnancy.stage = PregnancyStage.FIRST_TRIMESTER
        elif days_pregnant < 180:
            pregnancy.stage = PregnancyStage.SECOND_TRIMESTER
        else:
            pregnancy.stage = PregnancyStage.THIRD_TRIMESTER
            
        # Update pregnancy health
        pregnancy.health *= (1.0 - pregnancy.stress_level * 0.1)
        pregnancy.nutrition_level = min(1.0, pregnancy.nutrition_level + 
                                     (agent.needs.hunger - 0.5) * 0.1)
        
        # Check for birth
        if days_pregnant >= 270:  # 9 months
            self._handle_birth(agent, pregnancy)
            
    def _update_resources(self, agent: 'Agent', time_delta: float, world_state: Dict):
        """Update resource gathering and consumption."""
        # Find nearby resources
        nearby_resources = self._find_nearby_resources(agent.longitude, agent.latitude, 5)
        
        # Gather resources based on agent's capabilities
        for resource in nearby_resources:
            if self._can_gather_resource(agent, resource):
                amount = self._calculate_gather_amount(agent, resource)
                self._gather_resource(agent, resource, amount)
                
        # Consume resources
        self._consume_resources(agent, time_delta)
        
    def _should_die(self, agent: 'Agent') -> bool:
        """Check if agent should die."""
        # Check age
        if agent.age > agent.lifespan:
            return True
            
        # Check health
        if agent.health <= 0:
            return True
            
        # Check needs
        if agent.needs.hunger <= 0 or agent.needs.thirst <= 0:
            return True
            
        # Random chance based on age and health
        death_chance = (1.0 - agent.health) * (agent.age / agent.lifespan)
        return random.random() < death_chance
        
    def _handle_death(self, agent: 'Agent'):
        """Handle agent death."""
        death_record = {
            "agent_id": agent.id,
            "age": agent.age,
            "cause": self._determine_death_cause(agent),
            "timestamp": datetime.now(),
            "location": agent.position,
            "inventory": agent.inventory,
            "family": {
                "parents": agent.parents,
                "children": agent.children,
                "mate": agent.mate
            }
        }
        
        self.death_records.append(death_record)
        
        # Notify family and tribe
        self._notify_death(agent)
        
    def _can_reproduce(self, agent: 'Agent') -> bool:
        """Enhanced check if agent can reproduce."""
        if agent.life_stage not in [LifeStage.ADULT]:
            return False
            
        if agent.health < 0.7:
            return False
            
        if agent.needs.hunger < 0.7 or agent.needs.thirst < 0.7:
            return False
            
        # Check if agent is already pregnant
        if agent.id in self.pregnancies:
            return False
            
        # Check if agent is in courtship cooldown
        if agent.id in self.courtships:
            courtship = self.courtships[agent.id]
            if courtship.is_courting and time.time() - courtship.last_courtship_time < courtship.courtship_cooldown:
                return False
                
        return True
        
    def _attempt_reproduction(self, agent: 'Agent', world_state: Dict):
        """Attempt reproduction with mate."""
        if not agent.mate:
            return
            
        mate = world_state["agents"].get(agent.mate)
        if not mate or not self._can_reproduce(mate):
            return
            
        # Check if mate is nearby
        if not self._is_nearby(agent.position, mate.position):
            return
            
        # Chance of conception based on health and needs
        conception_chance = (agent.health + mate.health) / 2
        if random.random() < conception_chance:
            self._start_pregnancy(agent, mate)
            
    def _start_pregnancy(self, mother: 'Agent', father: 'Agent'):
        """Start a new pregnancy."""
        pregnancy = Pregnancy(
            start_date=datetime.now(),
            father_id=father.id
        )
        
        self.pregnancies[mother.id] = pregnancy
        
        # Update needs and emotions
        mother.needs.hunger *= 1.2  # Increased hunger
        mother.emotions.process_experience(
            "Started pregnancy",
            {"father": father.id},
            mother.to_dict()
        )
        
    def _handle_birth(self, mother: 'Agent', pregnancy: Pregnancy):
        """Enhanced birth handling with family relationship updates."""
        # Create new agent with inherited genes
        father = self.world.agents.get(pregnancy.father_id)
        new_agent = self._create_child(mother, father)
        
        # Record birth
        birth_record = {
            "agent_id": new_agent.id,
            "parents": {
                "mother": mother.id,
                "father": father.id if father else None
            },
            "timestamp": datetime.now(),
            "location": mother.position,
            "health": new_agent.health,
            "genes": new_agent.genes.__dict__
        }
        
        self.birth_records.append(birth_record)
        
        # Update family relationships
        self._update_relationship(mother.id, new_agent.id, "parent", 50.0)
        self._update_relationship(new_agent.id, mother.id, "child", 50.0)
        
        if father:
            self._update_relationship(father.id, new_agent.id, "parent", 50.0)
            self._update_relationship(new_agent.id, father.id, "child", 50.0)
            
        # Update siblings
        for child_id in mother.children:
            if child_id != new_agent.id:
                self._update_relationship(new_agent.id, child_id, "sibling", 30.0)
                self._update_relationship(child_id, new_agent.id, "sibling", 30.0)
                
        # Remove pregnancy
        del self.pregnancies[mother.id]
        
        # Update mother's needs and emotions
        mother.needs.hunger *= 0.8
        mother.emotions.process_experience(
            "Gave birth",
            {"child": new_agent.id},
            mother.to_dict()
        )
        
        # Log the birth
        self.world.log_event("agent_birth", {
            "agent_id": new_agent.id,
            "mother_id": mother.id,
            "father_id": father.id if father else None,
            "location": mother.position
        })
        
    def _create_child(self, mother: 'Agent', father: Optional['Agent']) -> 'Agent':
        """Create a new child agent with inherited genes."""
        # Inherit genes from parents
        genes = {}
        for gene in mother.genes.__dict__:
            if father:
                # Mix genes from both parents
                genes[gene] = (mother.genes.__dict__[gene] + 
                             father.genes.__dict__[gene]) / 2
            else:
                # Inherit from mother only
                genes[gene] = mother.genes.__dict__[gene]
                
            # Add random mutation
            genes[gene] = max(0.0, min(1.0, 
                genes[gene] + random.uniform(-0.1, 0.1)))
                
        # Create new agent
        return Agent(
            id=str(uuid.uuid4()),
            name=f"Child of {mother.name}",
            position=mother.position,
            genes=genes
        )
        
    def _find_nearby_resources(self, longitude: float, latitude: float, radius: float) -> List[Resource]:
        """Find resources within radius of position"""
        nearby_resources = []
        for resource in self.world.resources.get_resources():
            distance = self.world.get_distance(longitude, latitude, resource.longitude, resource.latitude)
            if distance <= radius:
                nearby_resources.append(resource)
        return nearby_resources
        
    def _can_gather_resource(self, agent: 'Agent', resource: Resource) -> bool:
        """Check if agent can gather the resource."""
        # Check if resource is available
        if resource.amount <= 0:
            return False
            
        # Check if agent has necessary tools
        if resource.type in agent.tools:
            return True
            
        # Some resources can be gathered without tools
        return resource.type in ["berries", "water", "herbs"]
        
    def _calculate_gather_amount(self, agent: 'Agent', resource: Resource) -> float:
        """Calculate how much of the resource the agent can gather."""
        base_amount = 0.1  # Base gathering amount
        
        # Modify based on agent's strength and tools
        if resource.type in agent.tools:
            base_amount *= 2.0
            
        base_amount *= agent.genes.strength
        
        # Don't gather more than available
        return min(base_amount, resource.amount)
        
    def _gather_resource(self, agent: 'Agent', resource: Resource, amount: float):
        """Gather resources and update agent's inventory."""
        resource.amount -= amount
        resource.last_harvested = datetime.now()
        
        if resource.type not in agent.inventory:
            agent.inventory[resource.type] = 0.0
            
        agent.inventory[resource.type] += amount
        
    def _consume_resources(self, agent: 'Agent', time_delta: float):
        """Consume resources to satisfy needs."""
        # Consume food
        if "food" in agent.inventory and agent.inventory["food"] > 0:
            consumed = min(0.1 * time_delta, agent.inventory["food"])
            agent.inventory["food"] -= consumed
            agent.needs.hunger = min(1.0, agent.needs.hunger + consumed)
            
        # Consume water
        if "water" in agent.inventory and agent.inventory["water"] > 0:
            consumed = min(0.2 * time_delta, agent.inventory["water"])
            agent.inventory["water"] -= consumed
            agent.needs.thirst = min(1.0, agent.needs.thirst + consumed)
            
    def _determine_death_cause(self, agent: 'Agent') -> str:
        """Determine the cause of death."""
        if agent.age > agent.lifespan:
            return "old_age"
        elif agent.health <= 0:
            return "health"
        elif agent.needs.hunger <= 0:
            return "starvation"
        elif agent.needs.thirst <= 0:
            return "dehydration"
        else:
            return "unknown"
            
    def _notify_death(self, agent: 'Agent'):
        """Notify family and tribe of death."""
        # Notify family
        for family_id in agent.parents + agent.children:
            if family_id in self.world.agents:
                family_member = self.world.agents[family_id]
                family_member.emotions.process_experience(
                    f"Family member {agent.name} died",
                    {"relationship": self._get_relationship(agent, family_member)},
                    family_member.to_dict()
                )
                
        # Notify tribe
        if agent.tribe:
            for tribe_member in self.world.get_tribe_members(agent.tribe):
                if tribe_member.id != agent.id:
                    tribe_member.emotions.process_experience(
                        f"Tribe member {agent.name} died",
                        {"relationship": "tribe_member"},
                        tribe_member.to_dict()
                    )
                    
    def _get_relationship(self, agent1: 'Agent', agent2: 'Agent') -> str:
        """Get the relationship between two agents."""
        if agent2.id in agent1.parents:
            return "parent"
        elif agent2.id in agent1.children:
            return "child"
        elif agent2.id == agent1.mate:
            return "mate"
        else:
            return "unknown"
            
    def _is_nearby(self, pos1: Tuple[int, int], pos2: Tuple[int, int], 
                  max_distance: int = 5) -> bool:
        """Check if two positions are nearby."""
        return abs(pos1[0] - pos2[0]) <= max_distance and \
               abs(pos1[1] - pos2[1]) <= max_distance

    def _find_potential_mate(self, agent: 'Agent', world_state: Dict) -> Optional['Agent']:
        """Find a suitable mate based on various factors."""
        potential_mates = []
        
        for other_id, other_agent in world_state["agents"].items():
            if other_id == agent.id:
                continue
                
            # Basic compatibility checks
            if not self._can_reproduce(other_agent):
                continue
                
            # Check if already in a relationship
            if other_agent.mate:
                continue
                
            # Calculate compatibility score
            compatibility = self._calculate_compatibility(agent, other_agent)
            if compatibility > 0.5:  # Minimum compatibility threshold
                potential_mates.append((other_agent, compatibility))
                
        if not potential_mates:
            return None
            
        # Sort by compatibility and return the best match
        potential_mates.sort(key=lambda x: x[1], reverse=True)
        return potential_mates[0][0]
        
    def _calculate_compatibility(self, agent1: 'Agent', agent2: 'Agent') -> float:
        """Calculate compatibility between two agents."""
        compatibility = 0.0
        
        # Genetic compatibility
        gene_compatibility = sum(
            abs(getattr(agent1.genes, gene) - getattr(agent2.genes, gene))
            for gene in agent1.genes.__dataclass_fields__
        ) / len(agent1.genes.__dataclass_fields__)
        compatibility += (1.0 - gene_compatibility) * 0.3
        
        # Personality compatibility
        personality_compatibility = sum(
            abs(getattr(agent1.personality, trait) - getattr(agent2.personality, trait))
            for trait in agent1.personality.__dataclass_fields__
        ) / len(agent1.personality.__dataclass_fields__)
        compatibility += (1.0 - personality_compatibility) * 0.3
        
        # Social compatibility
        if agent1.tribe == agent2.tribe:
            compatibility += 0.2
            
        # Age compatibility
        age_diff = abs(agent1.age - agent2.age)
        if age_diff < 5:
            compatibility += 0.1
        elif age_diff < 10:
            compatibility += 0.05
            
        return min(1.0, compatibility)
        
    def _initiate_courtship(self, agent: 'Agent', target: 'Agent'):
        """Initiate courtship with another agent."""
        if agent.id not in self.courtships:
            self.courtships[agent.id] = CourtshipState()
            
        courtship = self.courtships[agent.id]
        courtship.is_courting = True
        courtship.courtship_target = target.id
        courtship.courtship_progress = 0.0
        courtship.last_courtship_time = time.time()
        courtship.courtship_cooldown = random.uniform(3600, 7200)  # 1-2 hours
        
        # Add courtship action
        action = random.choice([
            "gift_giving",
            "dancing",
            "singing",
            "storytelling",
            "hunting_together",
            "gathering_together"
        ])
        courtship.courtship_actions.append(action)
        
        # Update relationship
        self._update_relationship(agent.id, target.id, "potential_mate", 10.0)
        
    def _update_courtship(self, agent: 'Agent', time_delta: float):
        """Update courtship progress."""
        if agent.id not in self.courtships:
            return
            
        courtship = self.courtships[agent.id]
        if not courtship.is_courting:
            return
            
        # Increase courtship progress
        courtship.courtship_progress += time_delta * 0.1
        
        # Check if courtship is successful
        if courtship.courtship_progress >= 100.0:
            target = self.world.agents.get_agent(courtship.courtship_target)
            if target and self._can_reproduce(target):
                self._form_mate_bond(agent, target)
                courtship.is_courting = False
                
    def _form_mate_bond(self, agent1: 'Agent', agent2: 'Agent'):
        """Form a mate bond between two agents."""
        agent1.mate = agent2.id
        agent2.mate = agent1.id
        
        # Create family relationships
        self._update_relationship(agent1.id, agent2.id, "mate", 50.0)
        self._update_relationship(agent2.id, agent1.id, "mate", 50.0)
        
        # Log the event
        self.world.log_event("mate_bond_formed", {
            "agent1_id": agent1.id,
            "agent2_id": agent2.id,
            "compatibility": self._calculate_compatibility(agent1, agent2)
        })
        
    def _update_relationship(self, agent_id: str, related_id: str, relationship_type: str, bond_change: float):
        """Update relationship between two agents."""
        if agent_id not in self.family_relationships:
            self.family_relationships[agent_id] = []
            
        # Find existing relationship
        relationship = None
        for rel in self.family_relationships[agent_id]:
            if rel.related_agent_id == related_id:
                relationship = rel
                break
                
        if relationship:
            # Update existing relationship
            relationship.bond_strength = min(100.0, relationship.bond_strength + bond_change)
            relationship.last_interaction_time = time.time()
        else:
            # Create new relationship
            relationship = FamilyRelationship(
                relationship_type=relationship_type,
                related_agent_id=related_id,
                bond_strength=bond_change,
                last_interaction_time=time.time()
            )
            self.family_relationships[agent_id].append(relationship)
            
    def to_dict(self) -> Dict:
        """Convert life cycle state to dictionary for serialization."""
        return {
            'pregnancies': {
                agent_id: {
                    'start_date': pregnancy.start_date.isoformat(),
                    'father_id': pregnancy.father_id,
                    'stage': pregnancy.stage.value,
                    'health': pregnancy.health,
                    'complications': pregnancy.complications,
                    'nutrition_level': pregnancy.nutrition_level,
                    'stress_level': pregnancy.stress_level
                }
                for agent_id, pregnancy in self.pregnancies.items()
            },
            'resources': {
                resource_type: [
                    {
                        'type': resource.type,
                        'amount': resource.amount,
                        'quality': resource.quality,
                        'location': resource.location,
                        'last_harvested': resource.last_harvested.isoformat() if resource.last_harvested else None,
                        'regrowth_rate': resource.regrowth_rate
                    }
                    for resource in resources
                ]
                for resource_type, resources in self.resources.items()
            },
            'death_records': self.death_records,
            'birth_records': self.birth_records,
            'courtships': {
                agent_id: {
                    'is_courting': courtship.is_courting,
                    'courtship_target': courtship.courtship_target,
                    'courtship_progress': courtship.courtship_progress,
                    'courtship_actions': courtship.courtship_actions,
                    'last_courtship_time': courtship.last_courtship_time,
                    'courtship_cooldown': courtship.courtship_cooldown
                }
                for agent_id, courtship in self.courtships.items()
            },
            'family_relationships': {
                agent_id: [
                    {
                        'relationship_type': rel.relationship_type,
                        'related_agent_id': rel.related_agent_id,
                        'bond_strength': rel.bond_strength,
                        'last_interaction_time': rel.last_interaction_time,
                        'shared_memories': rel.shared_memories
                    }
                    for rel in relationships
                ]
                for agent_id, relationships in self.family_relationships.items()
            }
        } 