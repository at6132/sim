from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

class TechnologyCategory(Enum):
    BASIC = "basic"  # Fire, tools, shelter
    AGRICULTURE = "agriculture"  # Farming, irrigation
    ANIMAL_HUSBANDRY = "animal_husbandry"  # Domestication, breeding
    METALLURGY = "metallurgy"  # Bronze, iron, steel
    CONSTRUCTION = "construction"  # Buildings, roads, bridges
    TRANSPORTATION = "transportation"  # Wheels, carts, boats
    ENERGY = "energy"  # Steam, electricity, combustion
    MANUFACTURING = "manufacturing"  # Factories, assembly lines
    COMMUNICATION = "communication"  # Writing, printing, telegraph
    COMPUTING = "computing"  # Mechanical computers, electronics
    TOOLS = "tools"
    SHELTER = "shelter"
    CLOTHING = "clothing"
    MEDICINE = "medicine"
    WEAPONS = "weapons"
    CULTURE = "culture"
    GOVERNANCE = "governance"

@dataclass
class Technology:
    name: str
    category: TechnologyCategory
    description: str
    prerequisites: List[str]  # List of technology names required
    research_cost: float  # Time/effort required to research
    effects: Dict[str, float]  # Effects on various aspects (e.g., {"food_production": 1.2})
    discovered: bool = False
    research_progress: float = 0.0

@dataclass
class TechnologyTree:
    technologies: Dict[str, Technology] = field(default_factory=dict)
    discovered_technologies: Set[str] = field(default_factory=set)
    research_queue: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self._initialize_technologies()
    
    def _initialize_technologies(self):
        """Initialize the technology tree with basic technologies"""
        # Agriculture technologies
        self.technologies["basic_farming"] = Technology(
            name="Basic Farming",
            category=TechnologyCategory.AGRICULTURE,
            description="Basic understanding of planting and harvesting crops",
            prerequisites=[],
            research_cost=100.0,
            effects={"food_production": 1.2}
        )
        
        self.technologies["irrigation"] = Technology(
            name="Irrigation",
            category=TechnologyCategory.AGRICULTURE,
            description="Methods for watering crops",
            prerequisites=["basic_farming"],
            research_cost=150.0,
            effects={"food_production": 1.5, "water_efficiency": 1.3}
        )
        
        # Tools technologies
        self.technologies["basic_tools"] = Technology(
            name="Basic Tools",
            category=TechnologyCategory.TOOLS,
            description="Simple tools for gathering and processing resources",
            prerequisites=[],
            research_cost=50.0,
            effects={"resource_gathering": 1.2}
        )
        
        self.technologies["advanced_tools"] = Technology(
            name="Advanced Tools",
            category=TechnologyCategory.TOOLS,
            description="More sophisticated tools for better resource processing",
            prerequisites=["basic_tools"],
            research_cost=200.0,
            effects={"resource_gathering": 1.5, "crafting_efficiency": 1.3}
        )
        
        # Shelter technologies
        self.technologies["basic_shelter"] = Technology(
            name="Basic Shelter",
            category=TechnologyCategory.SHELTER,
            description="Simple structures for protection from elements",
            prerequisites=[],
            research_cost=80.0,
            effects={"shelter_quality": 1.2}
        )
        
        # Medicine technologies
        self.technologies["basic_medicine"] = Technology(
            name="Basic Medicine",
            category=TechnologyCategory.MEDICINE,
            description="Understanding of basic healing and disease prevention",
            prerequisites=[],
            research_cost=120.0,
            effects={"healing_rate": 1.2, "disease_resistance": 1.1}
        )
        
        # Weapons technologies
        self.technologies["basic_weapons"] = Technology(
            name="Basic Weapons",
            category=TechnologyCategory.WEAPONS,
            description="Simple weapons for hunting and defense",
            prerequisites=[],
            research_cost=100.0,
            effects={"hunting_efficiency": 1.2, "combat_strength": 1.2}
        )
        
        # Clothing technologies
        self.technologies["basic_clothing"] = Technology(
            name="Basic Clothing",
            category=TechnologyCategory.CLOTHING,
            description="Simple clothing for protection from elements",
            prerequisites=[],
            research_cost=60.0,
            effects={"temperature_resistance": 1.2}
        )
        
        # Transportation technologies
        self.technologies["basic_transportation"] = Technology(
            name="Basic Transportation",
            category=TechnologyCategory.TRANSPORTATION,
            description="Simple methods for moving goods and people",
            prerequisites=[],
            research_cost=150.0,
            effects={"movement_speed": 1.2, "carrying_capacity": 1.2}
        )
        
        # Communication technologies
        self.technologies["basic_communication"] = Technology(
            name="Basic Communication",
            category=TechnologyCategory.COMMUNICATION,
            description="Simple methods for sharing information",
            prerequisites=[],
            research_cost=70.0,
            effects={"information_sharing": 1.2}
        )
        
        # Culture technologies
        self.technologies["basic_culture"] = Technology(
            name="Basic Culture",
            category=TechnologyCategory.CULTURE,
            description="Simple forms of artistic and cultural expression",
            prerequisites=[],
            research_cost=90.0,
            effects={"happiness": 1.1, "social_cohesion": 1.1}
        )
        
        # Governance technologies
        self.technologies["basic_governance"] = Technology(
            name="Basic Governance",
            category=TechnologyCategory.GOVERNANCE,
            description="Simple methods for organizing society",
            prerequisites=[],
            research_cost=200.0,
            effects={"organization_efficiency": 1.2, "conflict_resolution": 1.1}
        )
    
    def get_available_technologies(self) -> List[Technology]:
        """Get list of technologies that can be researched (prerequisites met)"""
        available = []
        for tech in self.technologies.values():
            if not tech.discovered and all(p in self.discovered_technologies for p in tech.prerequisites):
                available.append(tech)
        return available
    
    def start_research(self, technology_name: str) -> bool:
        """Start researching a technology"""
        if technology_name in self.discovered_technologies:
            logger.warning(f"Technology {technology_name} already discovered")
            return False
            
        if technology_name not in self.technologies:
            logger.warning(f"Technology {technology_name} not found")
            return False
            
        tech = self.technologies[technology_name]
        if not all(p in self.discovered_technologies for p in tech.prerequisites):
            logger.warning(f"Prerequisites not met for {technology_name}")
            return False
            
        if technology_name not in self.research_queue:
            self.research_queue.append(technology_name)
            logger.info(f"Started researching {technology_name}")
            return True
        return False
    
    def update_research(self, research_points: float) -> List[str]:
        """Update research progress and return list of newly discovered technologies"""
        newly_discovered = []
        
        if not self.research_queue:
            return newly_discovered
            
        current_tech = self.technologies[self.research_queue[0]]
        current_tech.research_progress += research_points
        
        if current_tech.research_progress >= current_tech.research_cost:
            current_tech.discovered = True
            self.discovered_technologies.add(current_tech.name)
            newly_discovered.append(current_tech.name)
            self.research_queue.pop(0)
            logger.info(f"Discovered new technology: {current_tech.name}")
            
        return newly_discovered
    
    def get_technology_effects(self) -> Dict[str, float]:
        """Get combined effects of all discovered technologies"""
        effects = {}
        for tech_name in self.discovered_technologies:
            tech = self.technologies[tech_name]
            for effect, value in tech.effects.items():
                effects[effect] = effects.get(effect, 1.0) * value
        return effects
    
    def get_research_progress(self, technology_name: str) -> Optional[float]:
        """Get research progress for a specific technology"""
        if technology_name not in self.technologies:
            return None
        return self.technologies[technology_name].research_progress / self.technologies[technology_name].research_cost

    def to_dict(self) -> Dict:
        """Convert technology tree state to dictionary for serialization."""
        return {
            "technologies": {
                name: {
                    "name": tech.name,
                    "category": tech.category.value,
                    "description": tech.description,
                    "prerequisites": tech.prerequisites,
                    "research_cost": tech.research_cost,
                    "effects": tech.effects,
                    "discovered": tech.discovered,
                    "research_progress": tech.research_progress
                }
                for name, tech in self.technologies.items()
            },
            "discovered_technologies": list(self.discovered_technologies),
            "research_queue": self.research_queue
        }

class TechnologySystem:
    def __init__(self):
        # Technology categories
        self.categories = {
            "tools": set(),  # Basic tools and implements
            "agriculture": set(),  # Farming and food production
            "construction": set(),  # Building and architecture
            "transportation": set(),  # Movement and travel
            "communication": set(),  # Information exchange
            "medicine": set(),  # Health and healing
            "materials": set(),  # Material processing
            "energy": set(),  # Power generation
            "military": set(),  # Weapons and defense
            "science": set()  # Scientific knowledge
        }
        
        # Technology prerequisites
        self.prerequisites = {
            "fire": set(),
            "stone_tools": {"fire"},
            "agriculture": {"stone_tools"},
            "pottery": {"fire", "stone_tools"},
            "metallurgy": {"fire", "stone_tools"},
            "writing": {"pottery"},
            "wheel": {"stone_tools", "construction"},
            "irrigation": {"agriculture", "construction"},
            "sailing": {"construction", "materials"},
            "medicine": {"science"},
            "mathematics": {"writing"},
            "astronomy": {"mathematics", "science"},
            "architecture": {"construction", "mathematics"},
            "engineering": {"mathematics", "materials"},
            "chemistry": {"science", "materials"},
            "physics": {"mathematics", "science"},
            "biology": {"science", "medicine"},
            "electricity": {"physics", "materials"},
            "steam_power": {"engineering", "materials"},
            "industrial_machinery": {"steam_power", "engineering"},
            "electronics": {"electricity", "materials"},
            "computers": {"electronics", "mathematics"},
            "internet": {"computers", "communication"},
            "artificial_intelligence": {"computers", "mathematics"},
            "space_travel": {"physics", "engineering"},
            "genetic_engineering": {"biology", "computers"},
            "nuclear_power": {"physics", "engineering"},
            "quantum_computing": {"physics", "computers"},
            "nanotechnology": {"materials", "engineering"},
            "fusion_power": {"physics", "engineering"}
        }
        
        # Technology effects
        self.effects = {
            "fire": {
                "food_quality": 0.2,
                "survival_rate": 0.1,
                "tool_quality": 0.1
            },
            "stone_tools": {
                "hunting_efficiency": 0.3,
                "construction_quality": 0.2,
                "defense_capability": 0.2
            },
            "agriculture": {
                "food_production": 0.5,
                "population_growth": 0.3,
                "settlement_stability": 0.4
            },
            "pottery": {
                "food_storage": 0.3,
                "trade_capacity": 0.2,
                "artistic_expression": 0.2
            },
            "metallurgy": {
                "tool_quality": 0.4,
                "weapon_quality": 0.4,
                "construction_quality": 0.3
            },
            "writing": {
                "knowledge_preservation": 0.5,
                "communication_range": 0.4,
                "cultural_development": 0.3
            },
            "wheel": {
                "transportation_efficiency": 0.4,
                "trade_capacity": 0.3,
                "construction_capability": 0.2
            },
            "irrigation": {
                "agricultural_yield": 0.4,
                "settlement_stability": 0.3,
                "population_capacity": 0.3
            },
            "sailing": {
                "exploration_capability": 0.4,
                "trade_range": 0.5,
                "military_power": 0.3
            },
            "medicine": {
                "health_quality": 0.4,
                "lifespan": 0.3,
                "population_growth": 0.2
            },
            "mathematics": {
                "scientific_advancement": 0.4,
                "engineering_capability": 0.3,
                "trade_efficiency": 0.2
            },
            "astronomy": {
                "navigation_capability": 0.3,
                "scientific_understanding": 0.4,
                "cultural_development": 0.2
            },
            "architecture": {
                "construction_quality": 0.4,
                "settlement_capacity": 0.3,
                "cultural_expression": 0.3
            },
            "engineering": {
                "construction_capability": 0.4,
                "tool_quality": 0.3,
                "military_power": 0.3
            },
            "chemistry": {
                "material_quality": 0.4,
                "medicine_effectiveness": 0.3,
                "industrial_capability": 0.3
            },
            "physics": {
                "scientific_understanding": 0.5,
                "engineering_capability": 0.4,
                "energy_efficiency": 0.3
            },
            "biology": {
                "medicine_effectiveness": 0.4,
                "agricultural_yield": 0.3,
                "scientific_understanding": 0.3
            },
            "electricity": {
                "energy_availability": 0.5,
                "industrial_capability": 0.4,
                "quality_of_life": 0.3
            },
            "steam_power": {
                "industrial_capability": 0.5,
                "transportation_efficiency": 0.4,
                "energy_availability": 0.3
            },
            "industrial_machinery": {
                "production_efficiency": 0.5,
                "industrial_capability": 0.4,
                "economic_growth": 0.3
            },
            "electronics": {
                "communication_capability": 0.4,
                "computing_power": 0.5,
                "quality_of_life": 0.3
            },
            "computers": {
                "information_processing": 0.5,
                "scientific_advancement": 0.4,
                "industrial_efficiency": 0.3
            },
            "internet": {
                "communication_range": 0.5,
                "information_access": 0.5,
                "cultural_exchange": 0.4
            },
            "artificial_intelligence": {
                "computing_power": 0.5,
                "automation_capability": 0.5,
                "scientific_advancement": 0.4
            },
            "space_travel": {
                "exploration_capability": 0.5,
                "scientific_understanding": 0.5,
                "resource_access": 0.4
            },
            "genetic_engineering": {
                "medicine_effectiveness": 0.5,
                "agricultural_yield": 0.5,
                "biological_understanding": 0.5
            },
            "nuclear_power": {
                "energy_availability": 0.5,
                "military_power": 0.5,
                "industrial_capability": 0.4
            },
            "quantum_computing": {
                "computing_power": 0.5,
                "scientific_advancement": 0.5,
                "cryptography_capability": 0.5
            },
            "nanotechnology": {
                "material_quality": 0.5,
                "medicine_effectiveness": 0.5,
                "manufacturing_capability": 0.5
            },
            "fusion_power": {
                "energy_availability": 0.5,
                "sustainability": 0.5,
                "industrial_capability": 0.5
            }
        }
        
        # Technology discovery history
        self.discoveries = []
        
        # Current research focus
        self.research_focus = None
        
        # Research progress
        self.research_progress = 0.0
        
    def update(self, time_delta: float, resources: Dict, population: int):
        """Update technology system based on time and available resources"""
        # Update research progress
        if self.research_focus:
            self._update_research(time_delta, resources, population)
        
        # Check for new discoveries
        self._check_discoveries()
        
        # Update technology effects
        self._update_effects()
    
    def _update_research(self, time_delta: float, resources: Dict, population: int):
        """Update research progress"""
        # Base research rate
        base_rate = 0.001 * time_delta
        
        # Modify by available resources
        resource_modifier = min(1.0, sum(resources.values()) / 1000.0)
        
        # Modify by population
        population_modifier = min(1.0, population / 1000.0)
        
        # Calculate total progress
        progress = base_rate * resource_modifier * population_modifier
        
        # Add to research progress
        self.research_progress = min(1.0, self.research_progress + progress)
    
    def _check_discoveries(self):
        """Check if any new technologies have been discovered"""
        if self.research_focus and self.research_progress >= 1.0:
            self._discover_technology(self.research_focus)
            self.research_focus = None
            self.research_progress = 0.0
    
    def _discover_technology(self, technology: str):
        """Record a new technology discovery"""
        # Add to appropriate category
        for category, technologies in self.categories.items():
            if technology in self.prerequisites:
                technologies.add(technology)
                break
        
        # Record discovery
        self.discoveries.append({
            "technology": technology,
            "timestamp": datetime.now().isoformat(),
            "effects": self.effects.get(technology, {})
        })
    
    def _update_effects(self):
        """Update effects of all discovered technologies"""
        # This would be used to update various systems based on technology effects
        pass
    
    def get_available_technologies(self) -> List[str]:
        """Get list of technologies that can be researched"""
        available = []
        
        for tech, prereqs in self.prerequisites.items():
            if tech not in self._get_all_discovered_technologies():
                if all(p in self._get_all_discovered_technologies() for p in prereqs):
                    available.append(tech)
        
        return available
    
    def _get_all_discovered_technologies(self) -> Set[str]:
        """Get set of all discovered technologies"""
        discovered = set()
        for category in self.categories.values():
            discovered.update(category)
        return discovered
    
    def get_technology_effects(self) -> Dict:
        """Get combined effects of all discovered technologies"""
        effects = {}
        
        for tech in self._get_all_discovered_technologies():
            tech_effects = self.effects.get(tech, {})
            for effect, value in tech_effects.items():
                if effect not in effects:
                    effects[effect] = 0.0
                effects[effect] += value
        
        return effects
    
    def set_research_focus(self, technology: str) -> bool:
        """Set the current research focus"""
        if technology in self.get_available_technologies():
            self.research_focus = technology
            self.research_progress = 0.0
            return True
        return False
    
    def get_research_status(self) -> Dict:
        """Get current research status"""
        return {
            "focus": self.research_focus,
            "progress": self.research_progress,
            "available": self.get_available_technologies()
        }
    
    def to_dict(self) -> Dict:
        """Convert technology system to dictionary"""
        return {
            "categories": {k: list(v) for k, v in self.categories.items()},
            "discoveries": self.discoveries,
            "research_focus": self.research_focus,
            "research_progress": self.research_progress
        } 