from dataclasses import dataclass
from typing import Dict, List, Set, Optional
from enum import Enum
import random
import logging
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

class DiscoveryType(Enum):
    # Basic Discoveries
    FIRE = "fire"
    TOOLS = "tools"
    WEAPONS = "weapons"
    SHELTER = "shelter"
    CLOTHING = "clothing"
    
    # Resource Discoveries
    AGRICULTURE = "agriculture"
    MINING = "mining"
    METALLURGY = "metallurgy"
    POTTERY = "pottery"
    TEXTILES = "textiles"
    
    # Social Discoveries
    LANGUAGE = "language"
    WRITING = "writing"
    TRADE = "trade"
    GOVERNMENT = "government"
    RELIGION = "religion"
    
    # Scientific Discoveries
    MATHEMATICS = "mathematics"
    ASTRONOMY = "astronomy"
    MEDICINE = "medicine"
    ENGINEERING = "engineering"
    CHEMISTRY = "chemistry"

@dataclass
class Discovery:
    type: DiscoveryType
    name: str
    description: str
    prerequisites: List[DiscoveryType]
    difficulty: float  # 0-1 scale
    impact: Dict[str, float]  # Impact on various systems
    discovered_by: Optional[int] = None  # Agent ID who discovered it
    discovery_time: Optional[float] = None  # Time of discovery

class DiscoverySystem:
    def __init__(self, world):
        """Initialize the discovery system."""
        self.world = world
        self.discoveries: Dict[DiscoveryType, Discovery] = {}
        self.discovered: Set[DiscoveryType] = set()
        self._initialize_discoveries()
        
    def _initialize_discoveries(self) -> None:
        """Initialize all possible discoveries"""
        self.discoveries = {
            DiscoveryType.FIRE: Discovery(
                type=DiscoveryType.FIRE,
                name="Fire",
                description="The discovery of fire and its uses",
                prerequisites=[],
                difficulty=0.1,
                impact={
                    "survival": 0.8,
                    "technology": 0.5,
                    "social": 0.3
                }
            ),
            DiscoveryType.TOOLS: Discovery(
                type=DiscoveryType.TOOLS,
                name="Basic Tools",
                description="Creation of simple tools from stone and wood",
                prerequisites=[DiscoveryType.FIRE],
                difficulty=0.2,
                impact={
                    "survival": 0.6,
                    "technology": 0.7,
                    "social": 0.2
                }
            ),
            DiscoveryType.WEAPONS: Discovery(
                type=DiscoveryType.WEAPONS,
                name="Weapons",
                description="Development of hunting and defensive weapons",
                prerequisites=[DiscoveryType.TOOLS],
                difficulty=0.3,
                impact={
                    "survival": 0.7,
                    "technology": 0.6,
                    "social": 0.4,
                    "military": 0.8
                }
            ),
            DiscoveryType.SHELTER: Discovery(
                type=DiscoveryType.SHELTER,
                name="Shelter",
                description="Construction of permanent shelters",
                prerequisites=[DiscoveryType.TOOLS],
                difficulty=0.3,
                impact={
                    "survival": 0.8,
                    "technology": 0.5,
                    "social": 0.6
                }
            ),
            DiscoveryType.CLOTHING: Discovery(
                type=DiscoveryType.CLOTHING,
                name="Clothing",
                description="Creation of clothing from animal hides and plant fibers",
                prerequisites=[DiscoveryType.TOOLS],
                difficulty=0.2,
                impact={
                    "survival": 0.7,
                    "technology": 0.4,
                    "social": 0.5
                }
            ),
            DiscoveryType.AGRICULTURE: Discovery(
                type=DiscoveryType.AGRICULTURE,
                name="Agriculture",
                description="Domestication of plants and farming techniques",
                prerequisites=[DiscoveryType.TOOLS, DiscoveryType.SHELTER],
                difficulty=0.5,
                impact={
                    "survival": 0.9,
                    "technology": 0.7,
                    "social": 0.8,
                    "population": 0.9
                }
            ),
            DiscoveryType.MINING: Discovery(
                type=DiscoveryType.MINING,
                name="Mining",
                description="Extraction of minerals and metals from the earth",
                prerequisites=[DiscoveryType.TOOLS, DiscoveryType.AGRICULTURE],
                difficulty=0.6,
                impact={
                    "technology": 0.8,
                    "social": 0.6,
                    "military": 0.7
                }
            ),
            DiscoveryType.METALLURGY: Discovery(
                type=DiscoveryType.METALLURGY,
                name="Metallurgy",
                description="Processing of metals and creation of alloys",
                prerequisites=[DiscoveryType.MINING, DiscoveryType.FIRE],
                difficulty=0.7,
                impact={
                    "technology": 0.9,
                    "military": 0.8,
                    "social": 0.7
                }
            ),
            DiscoveryType.POTTERY: Discovery(
                type=DiscoveryType.POTTERY,
                name="Pottery",
                description="Creation of ceramic vessels and containers",
                prerequisites=[DiscoveryType.FIRE],
                difficulty=0.4,
                impact={
                    "technology": 0.6,
                    "social": 0.5,
                    "survival": 0.5
                }
            ),
            DiscoveryType.TEXTILES: Discovery(
                type=DiscoveryType.TEXTILES,
                name="Textiles",
                description="Weaving and creation of fabric",
                prerequisites=[DiscoveryType.CLOTHING, DiscoveryType.AGRICULTURE],
                difficulty=0.5,
                impact={
                    "technology": 0.7,
                    "social": 0.8,
                    "survival": 0.6
                }
            ),
            DiscoveryType.LANGUAGE: Discovery(
                type=DiscoveryType.LANGUAGE,
                name="Language",
                description="Development of complex communication",
                prerequisites=[],
                difficulty=0.2,
                impact={
                    "social": 0.9,
                    "technology": 0.3,
                    "survival": 0.4
                }
            ),
            DiscoveryType.WRITING: Discovery(
                type=DiscoveryType.WRITING,
                name="Writing",
                description="Creation of written language and record keeping",
                prerequisites=[DiscoveryType.LANGUAGE],
                difficulty=0.6,
                impact={
                    "social": 0.9,
                    "technology": 0.8,
                    "knowledge": 0.9
                }
            ),
            DiscoveryType.TRADE: Discovery(
                type=DiscoveryType.TRADE,
                name="Trade",
                description="Establishment of trade networks and commerce",
                prerequisites=[DiscoveryType.LANGUAGE, DiscoveryType.AGRICULTURE],
                difficulty=0.4,
                impact={
                    "social": 0.8,
                    "technology": 0.6,
                    "economy": 0.9
                }
            ),
            DiscoveryType.GOVERNMENT: Discovery(
                type=DiscoveryType.GOVERNMENT,
                name="Government",
                description="Development of social organization and leadership",
                prerequisites=[DiscoveryType.LANGUAGE, DiscoveryType.AGRICULTURE],
                difficulty=0.5,
                impact={
                    "social": 0.9,
                    "military": 0.7,
                    "economy": 0.8
                }
            ),
            DiscoveryType.RELIGION: Discovery(
                type=DiscoveryType.RELIGION,
                name="Religion",
                description="Development of spiritual beliefs and practices",
                prerequisites=[DiscoveryType.LANGUAGE],
                difficulty=0.3,
                impact={
                    "social": 0.8,
                    "culture": 0.9,
                    "morale": 0.7
                }
            ),
            DiscoveryType.MATHEMATICS: Discovery(
                type=DiscoveryType.MATHEMATICS,
                name="Mathematics",
                description="Development of numerical systems and calculations",
                prerequisites=[DiscoveryType.WRITING],
                difficulty=0.7,
                impact={
                    "technology": 0.9,
                    "science": 0.9,
                    "economy": 0.8
                }
            ),
            DiscoveryType.ASTRONOMY: Discovery(
                type=DiscoveryType.ASTRONOMY,
                name="Astronomy",
                description="Study of celestial bodies and navigation",
                prerequisites=[DiscoveryType.MATHEMATICS],
                difficulty=0.8,
                impact={
                    "technology": 0.8,
                    "science": 0.9,
                    "navigation": 0.9
                }
            ),
            DiscoveryType.MEDICINE: Discovery(
                type=DiscoveryType.MEDICINE,
                name="Medicine",
                description="Development of healing practices and treatments",
                prerequisites=[DiscoveryType.WRITING, DiscoveryType.CHEMISTRY],
                difficulty=0.8,
                impact={
                    "survival": 0.9,
                    "science": 0.8,
                    "population": 0.8
                }
            ),
            DiscoveryType.ENGINEERING: Discovery(
                type=DiscoveryType.ENGINEERING,
                name="Engineering",
                description="Application of scientific principles to construction",
                prerequisites=[DiscoveryType.MATHEMATICS, DiscoveryType.METALLURGY],
                difficulty=0.8,
                impact={
                    "technology": 0.9,
                    "infrastructure": 0.9,
                    "military": 0.8
                }
            ),
            DiscoveryType.CHEMISTRY: Discovery(
                type=DiscoveryType.CHEMISTRY,
                name="Chemistry",
                description="Study of matter and its transformations",
                prerequisites=[DiscoveryType.MATHEMATICS, DiscoveryType.METALLURGY],
                difficulty=0.9,
                impact={
                    "technology": 0.9,
                    "science": 0.9,
                    "medicine": 0.8
                }
            )
        }
        
    def get_available_discoveries(self, agent_id: int, 
                                known_discoveries: Set[DiscoveryType]) -> List[Discovery]:
        """Get discoveries available to an agent based on prerequisites"""
        available = []
        for discovery in self.discoveries.values():
            if (discovery.type not in known_discoveries and
                all(prereq in known_discoveries for prereq in discovery.prerequisites)):
                available.append(discovery)
        return available
        
    def attempt_discovery(self, agent_id: int, discovery_type: DiscoveryType,
                         agent_intelligence: float, agent_creativity: float) -> bool:
        """Attempt to make a discovery"""
        if discovery_type in self.discovered:
            return False
            
        discovery = self.discoveries[discovery_type]
        
        # Calculate success probability based on agent attributes and discovery difficulty
        success_chance = (agent_intelligence * 0.6 + agent_creativity * 0.4) * (1 - discovery.difficulty)
        
        if random.random() < success_chance:
            self.discovered.add(discovery_type)
            discovery.discovered_by = agent_id
            discovery.discovery_time = 0.0  # Set to current time
            
            logger.info(f"Agent {agent_id} discovered {discovery.name}")
            return True
            
        return False
        
    def get_discovery_impact(self, discovery_type: DiscoveryType) -> Dict[str, float]:
        """Get the impact of a discovery on various systems"""
        return self.discoveries[discovery_type].impact
        
    def get_discovered_technologies(self) -> Set[DiscoveryType]:
        """Get all discovered technologies"""
        return self.discovered
        
    def get_discovery_prerequisites(self, discovery_type: DiscoveryType) -> List[DiscoveryType]:
        """Get prerequisites for a discovery"""
        return self.discoveries[discovery_type].prerequisites
        
    def get_discovery_difficulty(self, discovery_type: DiscoveryType) -> float:
        """Get the difficulty of a discovery"""
        return self.discoveries[discovery_type].difficulty
        
    def get_discovery_by_agent(self, agent_id: int) -> List[Discovery]:
        """Get all discoveries made by a specific agent"""
        return [
            discovery for discovery in self.discoveries.values()
            if discovery.discovered_by == agent_id
        ]

    def to_dict(self) -> Dict:
        """Convert discovery system state to dictionary for serialization."""
        return {
            "discoveries": {
                d_type.value: {
                    "name": d.name,
                    "description": d.description,
                    "prerequisites": [p.value for p in d.prerequisites],
                    "difficulty": d.difficulty,
                    "impact": d.impact,
                    "discovered_by": d.discovered_by,
                    "discovery_time": d.discovery_time
                }
                for d_type, d in self.discoveries.items()
            },
            "discovered": [d.value for d in self.discovered]
        }

    def get_state(self) -> Dict:
        """Get the current state of the discovery system for the web interface."""
        return {
            'discoveries': {
                discovery_type.value: {
                    'name': discovery.name,
                    'description': discovery.description,
                    'difficulty': discovery.difficulty,
                    'impact': discovery.impact,
                    'discovered': discovery_type in self.discovered,
                    'discovered_by': discovery.discovered_by,
                    'discovery_time': discovery.discovery_time,
                    'prerequisites': [p.value for p in discovery.prerequisites]
                }
                for discovery_type, discovery in self.discoveries.items()
            },
            'discovered_count': len(self.discovered),
            'total_discoveries': len(self.discoveries)
        } 