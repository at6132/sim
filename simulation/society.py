from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import random
from datetime import datetime
import logging
import uuid
import time

logger = logging.getLogger(__name__)

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
    roles: Dict[int, SocialRole]  # Agent ID to role mapping
    relationships: Dict[Tuple[int, int], Relationship]  # (agent1_id, agent2_id) to relationship
    territory: List[Tuple[int, int]]  # List of territory coordinates
    laws: Dict[str, float]  # Law name to enforcement strength

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
        # Use root logger to ensure events are printed
        root_logger = logging.getLogger()
        root_logger.info(f"Society Event - {event_type}: {data}")
        
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
        """Convert society state to dictionary for serialization."""
        return {
            "settlements": {
                settlement_id: {
                    "id": settlement.id,
                    "name": settlement.name,
                    "longitude": settlement.longitude,
                    "latitude": settlement.latitude,
                    "population": settlement.population,
                    "culture": settlement.culture,
                    "type": settlement.type,
                    "structures": settlement.structures,
                    "residents": list(settlement.residents),
                    "resources": settlement.resources,
                    "created_at": settlement.created_at,
                    "last_update": settlement.last_update
                }
                for settlement_id, settlement in self.settlements.items()
            },
            "social_groups": {
                group_id: {
                    "id": group.id,
                    "name": group.name,
                    "type": group.type.value,
                    "leader_id": group.leader_id,
                    "members": group.members,
                    "settlements": group.settlements,
                    "culture": group.culture.value,
                    "beliefs": group.beliefs,
                    "traditions": group.traditions,
                    "language": group.language,
                    "technology_level": group.technology_level
                }
                for group_id, group in self.social_groups.items()
            },
            "trade_routes": self.trade_routes,
            "cultural_developments": self.cultural_developments,
            "languages": self.languages,
            "religions": self.religions,
            "art_forms": self.art_forms,
            "governments": self.governments
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
                self._initialize_relationship(agent_id, member_id, group)
                
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
            self._remove_relationship(agent_id, member_id)
            
        logger.info(f"Removed agent {agent_id} from group {group_name}")
        return True
        
    def _initialize_relationship(self, agent1_id: int, agent2_id: int, group: SocialGroup) -> None:
        """Initialize a relationship between two agents"""
        # Determine relationship type based on roles and group culture
        if group.roles[agent1_id] == SocialRole.LEADER:
            rel_type = RelationshipType.MENTOR
        elif group.roles[agent2_id] == SocialRole.LEADER:
            rel_type = RelationshipType.STUDENT
        else:
            rel_type = random.choice(list(RelationshipType))
            
        relationship = Relationship(
            type=rel_type,
            strength=random.random(),
            trust=random.random(),
            history=[],
            last_interaction=0.0
        )
        
        group.relationships[(agent1_id, agent2_id)] = relationship
        group.relationships[(agent2_id, agent1_id)] = relationship
        
    def _remove_relationship(self, agent1_id: int, agent2_id: int) -> None:
        """Remove a relationship between two agents"""
        for group in self.social_groups.values():
            if (agent1_id, agent2_id) in group.relationships:
                del group.relationships[(agent1_id, agent2_id)]
            if (agent2_id, agent1_id) in group.relationships:
                del group.relationships[(agent2_id, agent1_id)]
                
    def update_relationship(self, agent1_id: int, agent2_id: int, 
                          interaction: str, strength_change: float, trust_change: float) -> None:
        """Update relationship between two agents based on interaction"""
        group_name = self.agent_groups.get(agent1_id)
        if not group_name or group_name != self.agent_groups.get(agent2_id):
            return
            
        group = self.social_groups[group_name]
        if (agent1_id, agent2_id) not in group.relationships:
            return
            
        relationship = group.relationships[(agent1_id, agent2_id)]
        relationship.strength = max(0.0, min(1.0, relationship.strength + strength_change))
        relationship.trust = max(0.0, min(1.0, relationship.trust + trust_change))
        relationship.history.append(interaction)
        relationship.last_interaction = 0.0  # Reset to current time
        
        # Update reverse relationship
        group.relationships[(agent2_id, agent1_id)] = relationship
        
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
        
    def get_relationship(self, agent1_id: int, agent2_id: int) -> Optional[Relationship]:
        """Get the relationship between two agents"""
        group_name = self.agent_groups.get(agent1_id)
        if not group_name or group_name != self.agent_groups.get(agent2_id):
            return None
        return self.social_groups[group_name].relationships.get((agent1_id, agent2_id))
        
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
        self.social_groups = {}
        self.settlements = {}
        self.religions = {}
        self.cultures = {}
        self.language_development = 0.0
        self.technology_level = 0.0
        self.civilization_level = 0.0
        self.events = []
        self.trade_routes = {}
        self.cultural_developments = {}
        self.languages = {}
        self.art_forms = {}
        self.governments = {}
        
    def initialize_society(self):
        """Initialize the society system."""
        logger.info("Initializing society system...")
        
        # Initialize social structures
        logger.info("Setting up social structures...")
        self.social_groups = {}
        logger.info("Social structures initialized")
        
        # Initialize settlements
        logger.info("Setting up settlements...")
        self.settlements = {}
        logger.info("Settlements initialized")
        
        # Initialize cultural systems
        logger.info("Setting up cultural systems...")
        self.religions = {}
        self.cultures = {}
        self.languages = {}
        self.art_forms = {}
        logger.info("Cultural systems initialized")
        
        # Initialize governance
        logger.info("Setting up governance systems...")
        self.governments = {}
        logger.info("Governance systems initialized")
        
        # Initialize trade and development
        logger.info("Setting up trade and development systems...")
        self.trade_routes = {}
        self.cultural_developments = {}
        logger.info("Trade and development systems initialized")
        
        # Initialize tracking variables
        logger.info("Initializing tracking variables...")
        self.language_development = 0.0
        self.technology_level = 0.0
        self.civilization_level = 0.0
        self.events = []
        logger.info("Tracking variables initialized")
        
        logger.info("Society system initialization complete")
        
    def verify_initialization(self) -> bool:
        """Verify that all required components are initialized."""
        logger.info("Verifying society system initialization...")
        
        # Check social structures
        if not self.social_groups:
            logger.warning("No social groups initialized")
            return False
            
        # Check settlements
        if not self.settlements:
            logger.warning("No settlements initialized")
            return False
            
        # Check cultural systems
        if not self.religions or not self.cultures or not self.languages:
            logger.warning("Cultural systems not fully initialized")
            return False
            
        # Check governance
        if not self.governments:
            logger.warning("Governance systems not initialized")
            return False
            
        # Check trade and development
        if not self.trade_routes or not self.cultural_developments:
            logger.warning("Trade and development systems not initialized")
            return False
            
        logger.info("Society system initialization verified successfully")
        return True
        
    def update(self, time_delta: float):
        """Update society system state."""
        # Update cultural evolution
        self._update_cultures(time_delta)
        
        # Update religious development
        self._update_religions(time_delta)
        
        # Update government systems
        self._update_governments(time_delta)
        
        # Update social dynamics
        self._update_social_classes(time_delta)
        
    def _update_cultures(self, time_delta: float):
        """Update cultural evolution."""
        # Implement cultural evolution logic
        pass
    
    def _update_religions(self, time_delta: float):
        """Update religious development."""
        # Implement religious development logic
        pass
        
    def _update_governments(self, time_delta: float):
        """Update government systems."""
        # Implement government system updates
        pass
        
    def _update_social_classes(self, time_delta: float):
        """Update social class dynamics."""
        # Implement social class dynamics
        pass
        
    def get_society_state(self) -> Dict:
        """Get current society system state."""
        return {
            "cultures": self.cultures,
            "religions": self.religions,
            "governments": self.governments,
            "social_classes": self.social_classes,
            "traditions": self.traditions,
            "languages": self.languages,
            "art_forms": self.art_forms
        } 