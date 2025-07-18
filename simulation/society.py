from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import random
from datetime import datetime
import logging
import uuid
import time
from .utils.logging_config import get_logger

logger = get_logger(__name__)

class SocialStructure(Enum):
    BAND = "band"           # Small family groups
    TRIBE = "tribe"         # Multiple families with shared culture
    CHIEFDOM = "chiefdom"   # Hierarchical society with leaders
    KINGDOM = "kingdom"     # Centralized rule with cities
    EMPIRE = "empire"       # Multiple kingdoms under one rule
    NATION = "nation"       # Modern state structure

class Culture(Enum):
    NOMADIC = "nomadic"     # Mobile lifestyle
    AGRARIAN = "agrarian"   # Farming-based
    MARITIME = "maritime"   # Sea-faring
    URBAN = "urban"         # City-dwelling
    INDUSTRIAL = "industrial"  # Manufacturing-based
    TECHNOLOGICAL = "technological"  # Tech-focused

class SocialRole(Enum):
    LEADER = "leader"
    ELDER = "elder"
    WARRIOR = "warrior"
    HUNTER = "hunter"
    GATHERER = "gatherer"
    CRAFTER = "crafter"
    SHAMAN = "shaman"
    CHILD = "child"
    ELDERLY = "elderly"

class RelationshipType(Enum):
    FAMILY = "family"
    FRIEND = "friend"
    ALLY = "ally"
    ENEMY = "enemy"
    MENTOR = "mentor"
    STUDENT = "student"
    TRADE_PARTNER = "trade_partner"
    RIVAL = "rival"

@dataclass
class Settlement:
    id: str
    name: str
    longitude: float
    latitude: float
    population: int
    culture: str
    type: str = "village"
    structures: List[str] = field(default_factory=list)
    residents: Set[str] = field(default_factory=set)
    resources: Dict[str, float] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Initialize settlement after creation."""
        self.resources = {
            "food": 100.0,
            "water": 100.0,
            "wood": 50.0,
            "stone": 50.0
        }

@dataclass
class Relationship:
    type: RelationshipType
    strength: float  # 0.0 to 1.0
    trust: float  # 0.0 to 1.0
    history: List[str]  # List of past interactions
    last_interaction: float  # Timestamp of last interaction

    def to_dict(self) -> Dict:
        """Convert relationship to dictionary."""
        return {
            "type": self.type.value,
            "strength": self.strength,
            "trust": self.trust,
            "history": self.history,
            "last_interaction": self.last_interaction
        }

@dataclass
class SocialGroup:
    id: str
    name: str
    type: SocialStructure
    leader_id: Optional[str]
    members: List[str]  # agent IDs
    settlements: List[str]  # settlement IDs
    culture: Culture
    beliefs: Dict[str, float]  # cultural values and beliefs
    traditions: List[str]
    language: str
    technology_level: int
    roles: Dict[str, SocialRole]  # Agent ID to role mapping
    relationships: Dict[str, Relationship]  # "agent1_id:agent2_id" to relationship
    territory: List[Tuple[float, float]]  # List of territory coordinates
    laws: Dict[str, float]  # Law name to enforcement strength

    def __post_init__(self):
        """Initialize social group after creation."""
        self.relationships = {}
        self.roles = {}
        self.territory = []
        self.laws = {}
        self.beliefs = {}
        self.traditions = []
        self.members = []
        self.settlements = []

    def get_relationship_key(self, agent1_id: str, agent2_id: str) -> str:
        """Get the key for a relationship between two agents."""
        return f"{agent1_id}:{agent2_id}"

    def add_relationship(self, agent1_id: str, agent2_id: str, relationship: Relationship) -> None:
        """Add a relationship between two agents."""
        key = self.get_relationship_key(agent1_id, agent2_id)
        self.relationships[key] = relationship

    def get_relationship(self, agent1_id: str, agent2_id: str) -> Optional[Relationship]:
        """Get the relationship between two agents."""
        key = self.get_relationship_key(agent1_id, agent2_id)
        return self.relationships.get(key)

    def remove_relationship(self, agent1_id: str, agent2_id: str) -> None:
        """Remove a relationship between two agents."""
        key = self.get_relationship_key(agent1_id, agent2_id)
        if key in self.relationships:
            del self.relationships[key]

    def to_dict(self) -> Dict:
        """Convert social group to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "leader_id": self.leader_id,
            "members": self.members,
            "settlements": self.settlements,
            "culture": self.culture.value,
            "beliefs": self.beliefs,
            "traditions": self.traditions,
            "language": self.language,
            "technology_level": self.technology_level,
            "roles": {str(k): v.value for k, v in self.roles.items()},
            "relationships": {k: v.to_dict() for k, v in self.relationships.items()},
            "territory": [f"{lon},{lat}" for lon, lat in self.territory],
            "laws": self.laws
        }

@dataclass
class SocietyTerritory:
    """Represents a territory claimed by a society"""
    center_longitude: float
    center_latitude: float
    radius: float  # in kilometers
    claimed_by: Optional[str] = None
    resources: Dict[str, float] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)

@dataclass
class Society:
    """Represents a society in the simulation"""
    id: str
    name: str
    leader_id: str
    members: List[str]
    territory: Optional[SocietyTerritory]
    culture: Dict[str, float]
    history: List[Dict]
    resources: Dict[str, float]
    relationships: Dict[str, float]  # society_id -> relationship value

    def __init__(self, world):
        self.world = world
        self.social_groups = {}
        self.settlements = {}
        self.religions = {}
        self.cultures = {}
        self.language_development = 0.0
        self.technology_level = 0.0
        self.civilization_level = 0.0
        self.events = []
        
    def create_initial_society(self, agent_ids, positions):
        """Create the initial society structure."""
        # Create first social group
        group_id = str(uuid.uuid4())
        self.social_groups[group_id] = SocialGroup(
            id=group_id,
            name="First Tribe",
            members=set(agent_ids),
            culture="tribal",
            beliefs={
                "cooperation": 0.7,
                "exploration": 0.8,
                "survival": 0.9
            },
            traditions=["oral_history", "hunting_rituals"],
            language="proto_language",
            technology_level=0,
            roles={},
            relationships={},
            territory=[],
            laws={}
        )
        
        # Create first settlement (camp)
        camp_id = f"camp_{len(self.settlements)}"
        camp = Settlement(
            id=camp_id,
            name="First Camp",
            longitude=positions[0][0],
            latitude=positions[0][1],
            population=len(agent_ids),
            culture="tribal",
            type="camp",
            structures=["shelter", "fire_pit"],
            residents=set(agent_ids),
            resources={},
            created_at=time.time(),
            last_update=time.time()
        )
        self.settlements[camp_id] = camp
        self.social_groups[group_id].settlements.append(camp_id)
        
        # Create first religion
        religion_id = str(uuid.uuid4())
        self.religions[religion_id] = {
            "deities": ["nature_spirit", "ancestor_spirit"],
            "rituals": ["offering", "prayer"],
            "beliefs": ["afterlife", "spirit_world"]
        }
        
        # Create first culture
        culture_id = str(uuid.uuid4())
        self.cultures[culture_id] = {
            'aggression': 0.5,
            'cooperation': 0.5,
            'innovation': 0.5,
            'tradition': 0.5
        }
        
        self.log_event("society_created", {
            "group_id": group_id,
            "settlement_id": camp_id,
            "religion_id": religion_id,
            "culture_id": culture_id
        })
        
    def log_event(self, event_type: str, data: Dict):
        """Log a society event."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        # Use standardized logger
        logger.info(f"Society Event - {event_type}: {data}")
        
    def get_state(self) -> Dict:
        """Get current society state."""
        return {
            "social_groups": {id: group.to_dict() for id, group in self.social_groups.items()},
            "settlements": {id: settlement.to_dict() for id, settlement in self.settlements.items()},
            "religions": {id: religion for id, religion in self.religions.items()},
            "cultures": {id: culture for id, culture in self.cultures.items()},
            "language_development": self.language_development,
            "technology_level": self.technology_level,
            "civilization_level": self.civilization_level,
            "events": self.events[-100:]  # Keep last 100 events
        }

    def is_in_territory(self, longitude: float, latitude: float) -> bool:
        """Check if a location is within the society's territory"""
        if not self.territory:
            return False
        distance = self.world.get_distance(
            longitude, latitude,
            self.territory.center_longitude,
            self.territory.center_latitude
        )
        return distance <= self.territory.radius

    def expand_territory(self, new_longitude: float, new_latitude: float, new_radius: float) -> None:
        """Expand the society's territory to include a new area"""
        if not self.territory:
            self.territory = SocietyTerritory(
                center_longitude=new_longitude,
                center_latitude=new_latitude,
                radius=new_radius,
                claimed_by=self.id
            )
        else:
            # Calculate new center as midpoint between old center and new location
            self.territory.center_longitude = (self.territory.center_longitude + new_longitude) / 2
            self.territory.center_latitude = (self.territory.center_latitude + new_latitude) / 2
            self.territory.radius = max(self.territory.radius, new_radius)

    def create_group(self, name: str, leader_id: str, longitude: float, latitude: float, radius: float = 10.0) -> None:
        """Create a new society group"""
        group_id = str(uuid.uuid4())
        self.social_groups[group_id] = SocialGroup(
            id=group_id,
            name=name,
            type=SocialStructure.BAND,
            leader_id=leader_id,
            members=[leader_id],
            settlements=[],
            culture=Culture.NOMADIC,
            beliefs={
                "cooperation": 0.7,
                "exploration": 0.8,
                "survival": 0.9
            },
            traditions=["oral_history", "hunting_rituals"],
            language="proto_language",
            technology_level=0,
            roles={},
            relationships={},
            territory=[],
            laws={}
        )
        self.history.append({
            'type': 'group_created',
            'group_id': group_id,
            'name': name,
            'leader_id': leader_id,
            'timestamp': time.time()
        })

    def update_social_structure(self, agent_id: str, group_id: str):
        """Update social structure based on population and development."""
        group = self.social_groups[group_id]
        
        # Check for social structure advancement
        if group.type == SocialStructure.BAND and len(group.members) >= 30:
            self._advance_to_tribe(group)
        elif group.type == SocialStructure.TRIBE and len(group.members) >= 100:
            self._advance_to_chiefdom(group)
        elif group.type == SocialStructure.CHIEFDOM and len(group.members) >= 500:
            self._advance_to_kingdom(group)
        elif group.type == SocialStructure.KINGDOM and len(group.members) >= 2000:
            self._advance_to_empire(group)
        elif group.type == SocialStructure.EMPIRE and len(group.members) >= 10000:
            self._advance_to_nation(group)

    def _advance_to_tribe(self, group: SocialGroup):
        """Advance a band to a tribe."""
        group.type = SocialStructure.TRIBE
        group.beliefs.update({
            "territory": 0.6,
            "ancestry": 0.7,
            "ritual": 0.5
        })
        group.traditions.extend(["territorial_markers", "ancestral_worship"])

    def _advance_to_chiefdom(self, group: SocialGroup):
        """Advance a tribe to a chiefdom."""
        group.type = SocialStructure.CHIEFDOM
        group.beliefs.update({
            "hierarchy": 0.8,
            "wealth": 0.6,
            "prestige": 0.7
        })
        group.traditions.extend(["chiefly_succession", "wealth_display"])

    def _advance_to_kingdom(self, group: SocialGroup):
        """Advance a chiefdom to a kingdom."""
        group.type = SocialStructure.KINGDOM
        group.beliefs.update({
            "divine_right": 0.8,
            "law": 0.9,
            "nobility": 0.7
        })
        group.traditions.extend(["royal_court", "legal_system"])

    def _advance_to_empire(self, group: SocialGroup):
        """Advance a kingdom to an empire."""
        group.type = SocialStructure.EMPIRE
        group.beliefs.update({
            "imperialism": 0.8,
            "centralization": 0.9,
            "cultural_unity": 0.7
        })
        group.traditions.extend(["imperial_administration", "cultural_assimilation"])

    def _advance_to_nation(self, group: SocialGroup):
        """Advance an empire to a nation."""
        group.type = SocialStructure.NATION
        group.beliefs.update({
            "nationalism": 0.8,
            "democracy": 0.7,
            "progress": 0.9
        })
        group.traditions.extend(["constitutional_government", "scientific_method"])

    def develop_settlement(self, settlement_id: str):
        """Develop a settlement based on population and technology."""
        settlement = self.settlements[settlement_id]
        
        # Check for settlement advancement
        if settlement.type == "camp" and settlement.population >= 50:
            self._advance_to_village(settlement)
        elif settlement.type == "village" and settlement.population >= 200:
            self._advance_to_town(settlement)
        elif settlement.type == "town" and settlement.population >= 1000:
            self._advance_to_city(settlement)
        elif settlement.type == "city" and settlement.population >= 5000:
            self._advance_to_metropolis(settlement)

    def _advance_to_village(self, settlement: Settlement):
        """Advance a camp to a village."""
        settlement.type = "village"
        settlement.structures.extend([
            "permanent_houses",
            "storage_buildings",
            "communal_areas"
        ])

    def _advance_to_town(self, settlement: Settlement):
        """Advance a village to a town."""
        settlement.type = "town"
        settlement.structures.extend([
            "marketplace",
            "religious_building",
            "defensive_walls",
            "craftsmen_quarters"
        ])

    def _advance_to_city(self, settlement: Settlement):
        """Advance a town to a city."""
        settlement.type = "city"
        settlement.structures.extend([
            "palace",
            "temple_complex",
            "aqueduct",
            "public_baths",
            "library"
        ])

    def _advance_to_metropolis(self, settlement: Settlement):
        """Advance a city to a metropolis."""
        settlement.type = "metropolis"
        settlement.structures.extend([
            "university",
            "theater",
            "stadium",
            "harbor",
            "industrial_district"
        ])

    def develop_culture(self, group_id: str):
        """Develop cultural aspects of a social group."""
        group = self.social_groups[group_id]
        
        # Develop language
        if group.language == "proto_language":
            self._develop_language(group)
            
        # Develop religion
        if "religion" not in group.beliefs:
            self._develop_religion(group)
            
        # Develop art
        if "art" not in group.traditions:
            self._develop_art(group)

    def _develop_language(self, group: SocialGroup):
        """Develop a more sophisticated language."""
        group.language = f"language_{len(self.languages)}"
        self.languages[group.language] = {
            "vocabulary": ["basic_terms", "family_terms", "nature_terms"],
            "grammar": "basic",
            "writing_system": None
        }

    def _develop_religion(self, group: SocialGroup):
        """Develop religious beliefs."""
        group.beliefs["religion"] = 0.5
        self.religions[group.id] = {
            "deities": ["nature_spirit", "ancestor_spirit"],
            "rituals": ["offering", "prayer"],
            "beliefs": ["afterlife", "spirit_world"]
        }

    def _develop_art(self, group: SocialGroup):
        """Develop artistic traditions."""
        group.traditions.append("art")
        self.art_forms[group.id] = [
            "body_painting",
            "stone_carving",
            "music"
        ]

    def to_dict(self) -> Dict:
        """Convert society system state to dictionary."""
        return {
            "social_groups": {
                group_id: {
                    "name": group["name"],
                    "members": group["members"],
                    "purpose": group["purpose"],
                    "influence": group["influence"]
                }
                for group_id, group in self.social_groups.items()
            },
            "settlements": {
                settlement_id: {
                    "name": settlement["name"],
                    "population": settlement["population"],
                    "location": settlement["location"],
                    "type": settlement["type"],
                    "resources": settlement["resources"]
                }
                for settlement_id, settlement in self.settlements.items()
            },
            "religions": self.religions,
            "languages": self.languages,
            "cultural_traits": self.cultural_traits
        }

    def add_member_to_group(self, group_name: str, agent_id: int, role: SocialRole) -> bool:
        """Add a member to a social group"""
        if group_name not in self.social_groups:
            logger.warning(f"Group {group_name} does not exist")
            return False
            
        group = self.social_groups[group_name]
        group.members.append(str(agent_id))
        group.roles[agent_id] = role
        self.agent_groups[agent_id] = group_name
        
        # Initialize relationships with existing members
        for member_id in group.members:
            if member_id != str(agent_id):
                self._initialize_relationship(str(agent_id), member_id, group)
                
        logger.info(f"Added agent {agent_id} to group {group_name} as {role.value}")
        return True
        
    def remove_member_from_group(self, group_name: str, agent_id: int) -> bool:
        """Remove a member from a social group"""
        if group_name not in self.social_groups:
            return False
            
        group = self.social_groups[group_name]
        if str(agent_id) not in group.members:
            return False
            
        group.members.remove(str(agent_id))
        del group.roles[agent_id]
        del self.agent_groups[agent_id]
        
        # Remove relationships with group members
        for member_id in list(group.members):
            self._remove_relationship(str(agent_id), member_id)
            
        logger.info(f"Removed agent {agent_id} from group {group_name}")
        return True
        
    def _initialize_relationship(self, agent1_id: str, agent2_id: str, group: SocialGroup) -> None:
        """Initialize a relationship between two agents"""
        # Determine relationship type based on roles and group culture
        if group.roles.get(agent1_id) == SocialRole.LEADER:
            rel_type = RelationshipType.MENTOR
        elif group.roles.get(agent2_id) == SocialRole.LEADER:
            rel_type = RelationshipType.STUDENT
        else:
            rel_type = random.choice(list(RelationshipType))
            
        relationship = Relationship(
            type=rel_type,
            strength=random.random(),
            trust=random.random(),
            history=[],
            last_interaction=time.time()
        )
        
        group.add_relationship(agent1_id, agent2_id, relationship)
        
    def _remove_relationship(self, agent1_id: str, agent2_id: str) -> None:
        """Remove a relationship between two agents"""
        for group in self.social_groups.values():
            group.remove_relationship(agent1_id, agent2_id)
                
    def update_relationship(self, agent1_id: str, agent2_id: str, 
                          interaction: str, strength_change: float, trust_change: float) -> None:
        """Update relationship between two agents based on interaction"""
        group_name = self.agent_groups.get(agent1_id)
        if not group_name or group_name != self.agent_groups.get(agent2_id):
            return
            
        group = self.social_groups[group_name]
        relationship = group.get_relationship(agent1_id, agent2_id)
        if not relationship:
            return
            
        relationship.strength = max(0.0, min(1.0, relationship.strength + strength_change))
        relationship.trust = max(0.0, min(1.0, relationship.trust + trust_change))
        relationship.history.append(interaction)
        relationship.last_interaction = time.time()
        
        logger.info(f"Updated relationship between {agent1_id} and {agent2_id}: {interaction}")
        
    def add_law(self, group_name: str, law_name: str, enforcement_strength: float) -> None:
        """Add a new law to a group"""
        if group_name not in self.social_groups:
            return
            
        self.social_groups[group_name].laws[law_name] = enforcement_strength
        logger.info(f"Added law {law_name} to group {group_name}")
        
    def remove_law(self, group_name: str, law_name: str) -> None:
        """Remove a law from a group"""
        if group_name not in self.social_groups:
            return
            
        if law_name in self.social_groups[group_name].laws:
            del self.social_groups[group_name].laws[law_name]
            logger.info(f"Removed law {law_name} from group {group_name}")
            
    def update_culture(self, group_name: str, trait: str, change: float) -> None:
        """Update a cultural trait for a group"""
        if group_name not in self.social_groups:
            return
            
        if trait in self.social_groups[group_name].culture:
            self.social_groups[group_name].culture[trait] = max(0.0, min(1.0, 
                self.social_groups[group_name].culture[trait] + change))
            logger.info(f"Updated cultural trait {trait} in group {group_name}")
            
    def get_group_members(self, group_name: str) -> Set[int]:
        """Get all members of a group"""
        return self.social_groups.get(group_name, SocialGroup("", [], {}, {}, [], {}, {})).members
        
    def get_agent_group(self, agent_id: int) -> Optional[str]:
        """Get the group an agent belongs to"""
        return self.agent_groups.get(agent_id)
        
    def get_agent_role(self, agent_id: int) -> Optional[SocialRole]:
        """Get the role of an agent in their group"""
        group_name = self.agent_groups.get(agent_id)
        if not group_name:
            return None
        return self.social_groups[group_name].roles.get(agent_id)
        
    def get_relationship(self, agent1_id: str, agent2_id: str) -> Optional[Relationship]:
        """Get the relationship between two agents"""
        group_name = self.agent_groups.get(agent1_id)
        if not group_name or group_name != self.agent_groups.get(agent2_id):
            return None
        return self.social_groups[group_name].get_relationship(agent1_id, agent2_id)
        
    def get_group_laws(self, group_name: str) -> Dict[str, float]:
        """Get all laws of a group"""
        return self.social_groups.get(group_name, SocialGroup("", [], {}, {}, [], {}, {})).laws
        
    def get_group_culture(self, group_name: str) -> Dict[str, float]:
        """Get cultural traits of a group"""
        return self.social_groups.get(group_name, SocialGroup("", [], {}, {}, [], {}, {})).culture

    def get_language_development(self) -> float:
        """Get the current language development level (0.0 to 1.0)."""
        if not self.social_groups:
            return 0.0
            
        # Calculate average language development across all groups
        total_development = 0.0
        for group in self.social_groups.values():
            # Base development on group's technology level and cultural development
            group_development = (
                group.technology_level * 0.4 +  # Technology contributes 40%
                len(group.traditions) * 0.1 +   # Each tradition adds 10%
                len(group.beliefs) * 0.1        # Each belief adds 10%
            )
            total_development += min(1.0, group_development)
            
        return total_development / len(self.social_groups)

class SocietySystem:
    def __init__(self, world):
        self.world = world
        self.logger = get_logger(__name__)
        
        # Initialize society components
        self.tribes = {}  # tribe_id -> tribe_data
        self.religions = {}  # religion_id -> religion_data
        self.languages = {}  # language_id -> language_data
        self.settlements = {}  # settlement_id -> settlement_data
        self.social_groups = {}  # group_id -> group_data
        self.cultural_traits = {}  # trait_id -> trait_data
        
        self.logger.info("Society system initialized")
    
    def initialize_society(self):
        """Initialize the society system with basic structures."""
        self.logger.info("Initializing society system...")
        
        # Initialize tribes
        self._initialize_tribes()
        
        # Initialize religions
        self._initialize_religions()
        
        # Initialize languages
        self._initialize_languages()
        
        # Initialize settlements
        self._initialize_settlements()
        
        # Initialize social groups
        self._initialize_social_groups()
        
        # Initialize cultural traits
        self._initialize_cultural_traits()
        
        self.logger.info("Society system initialization complete")
    
    def _initialize_tribes(self):
        """Initialize basic tribes."""
        self.logger.info("Initializing tribes...")
        
        # Create initial tribes
        self.tribes = {
            'tribe_1': {
                'name': 'Northern Hunters',
                'population': 100,
                'territory': [(0, 0), (1, 1)],
                'culture': 'hunter_gatherer',
                'resources': {'food': 50, 'tools': 20}
            },
            'tribe_2': {
                'name': 'River Farmers',
                'population': 150,
                'territory': [(2, 2), (3, 3)],
                'culture': 'agricultural',
                'resources': {'food': 100, 'tools': 30}
            }
        }
    
    def _initialize_religions(self):
        """Initialize basic religions."""
        self.logger.info("Initializing religions...")
        
        self.religions = {
            'religion_1': {
                'name': 'Nature Worship',
                'followers': 80,
                'beliefs': ['animism', 'nature_spirits'],
                'practices': ['seasonal_rituals', 'sacred_sites']
            },
            'religion_2': {
                'name': 'Ancestor Worship',
                'followers': 120,
                'beliefs': ['ancestral_spirits', 'reincarnation'],
                'practices': ['ancestral_offerings', 'lineage_tracking']
            }
        }
    
    def _initialize_languages(self):
        """Initialize basic languages."""
        self.logger.info("Initializing languages...")
        
        self.languages = {
            'lang_1': {
                'name': 'Northern Tongue',
                'speakers': 90,
                'vocabulary': {'basic': 100, 'advanced': 50},
                'dialects': ['north', 'south']
            },
            'lang_2': {
                'name': 'River Speech',
                'speakers': 110,
                'vocabulary': {'basic': 120, 'advanced': 60},
                'dialects': ['east', 'west']
            }
        }
    
    def _initialize_settlements(self):
        """Initialize basic settlements."""
        self.logger.info("Initializing settlements...")
        
        self.settlements = {
            'settlement_1': {
                'name': 'Northern Camp',
                'population': 50,
                'location': (0, 0),
                'type': 'hunting_camp',
                'resources': {'shelter': 20, 'food': 30}
            },
            'settlement_2': {
                'name': 'River Village',
                'population': 75,
                'location': (2, 2),
                'type': 'farming_village',
                'resources': {'shelter': 30, 'food': 50}
            }
        }
    
    def _initialize_social_groups(self):
        """Initialize basic social groups."""
        self.logger.info("Initializing social groups...")
        
        self.social_groups = {
            'group_1': {
                'name': 'Hunters Guild',
                'members': 30,
                'purpose': 'hunting',
                'influence': 0.6
            },
            'group_2': {
                'name': 'Farmers Collective',
                'members': 45,
                'purpose': 'farming',
                'influence': 0.7
            }
        }
    
    def _initialize_cultural_traits(self):
        """Initialize basic cultural traits."""
        self.logger.info("Initializing cultural traits...")
        
        self.cultural_traits = {
            'trait_1': {
                'name': 'Seasonal Migration',
                'prevalence': 0.8,
                'impact': {'mobility': 0.7, 'stability': 0.3}
            },
            'trait_2': {
                'name': 'Agricultural Innovation',
                'prevalence': 0.6,
                'impact': {'productivity': 0.8, 'stability': 0.6}
            }
        }
    
    def update(self, time_delta: float):
        """Update society state."""
        self.logger.debug(f"Updating society with time delta: {time_delta}")
        
        # Update tribes
        self._update_tribes(time_delta)
        
        # Update religions
        self._update_religions(time_delta)
        
        # Update languages
        self._update_languages(time_delta)
        
        # Update settlements
        self._update_settlements(time_delta)
        
        # Update social groups
        self._update_social_groups(time_delta)
        
        # Update cultural traits
        self._update_cultural_traits(time_delta)
    
    def _update_tribes(self, time_delta: float):
        """Update tribe states."""
        for tribe_id, tribe in self.tribes.items():
            # Update population
            growth_rate = 0.01 * time_delta
            tribe['population'] *= (1 + growth_rate)
            
            # Update resources
            for resource, amount in tribe['resources'].items():
                if resource == 'food':
                    tribe['resources'][resource] *= (1 - 0.05 * time_delta)
                else:
                    tribe['resources'][resource] *= (1 - 0.02 * time_delta)
    
    def _update_religions(self, time_delta: float):
        """Update religion states."""
        for religion_id, religion in self.religions.items():
            # Update follower count
            conversion_rate = 0.005 * time_delta
            religion['followers'] *= (1 + conversion_rate)
    
    def _update_languages(self, time_delta: float):
        """Update language states."""
        for language_id, language in self.languages.items():
            # Update vocabulary
            for level, count in language['vocabulary'].items():
                growth_rate = 0.002 * time_delta
                language['vocabulary'][level] *= (1 + growth_rate)
    
    def _update_settlements(self, time_delta: float):
        """Update settlement states."""
        for settlement_id, settlement in self.settlements.items():
            # Update population
            growth_rate = 0.01 * time_delta
            settlement['population'] *= (1 + growth_rate)
            
            # Update resources
            for resource, amount in settlement['resources'].items():
                if resource == 'food':
                    settlement['resources'][resource] *= (1 - 0.05 * time_delta)
                else:
                    settlement['resources'][resource] *= (1 - 0.02 * time_delta)
    
    def _update_social_groups(self, time_delta: float):
        """Update social group states."""
        for group_id, group in self.social_groups.items():
            # Update membership
            growth_rate = 0.005 * time_delta
            group['members'] *= (1 + growth_rate)
            
            # Update influence
            influence_change = 0.001 * time_delta
            group['influence'] = min(1.0, group['influence'] + influence_change)
    
    def _update_cultural_traits(self, time_delta: float):
        """Update cultural trait states."""
        for trait_id, trait in self.cultural_traits.items():
            # Update prevalence
            change_rate = 0.001 * time_delta
            trait['prevalence'] = min(1.0, trait['prevalence'] + change_rate)
    
    def get_state(self) -> Dict:
        """Get the current state of the society system."""
        return {
            'tribes': self.tribes,
            'religions': self.religions,
            'languages': self.languages,
            'settlements': self.settlements,
            'social_groups': self.social_groups,
            'cultural_traits': self.cultural_traits
        }

    def to_dict(self):
        """Convert society system state to dictionary."""
        return {
            "social_groups": {
                group_id: {
                    "name": group["name"],
                    "members": group["members"],
                    "purpose": group["purpose"],
                    "influence": group["influence"]
                }
                for group_id, group in self.social_groups.items()
            },
            "settlements": {
                settlement_id: {
                    "name": settlement["name"],
                    "population": settlement["population"],
                    "location": settlement["location"],
                    "type": settlement["type"],
                    "resources": settlement["resources"]
                }
                for settlement_id, settlement in self.settlements.items()
            },
            "religions": self.religions,
            "languages": self.languages,
            "cultural_traits": self.cultural_traits
        } 