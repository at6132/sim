from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
import random
import logging
import time

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
    FIRE = "fire"

@dataclass
class Technology:
    type: str  # Emergent technology type
    name: str
    description: str
    category: TechnologyCategory = None
    prerequisites: Set[str] = field(default_factory=set)
    difficulty: float = 0.0
    discovery_chance: float = 0.0
    required_resources: Dict[str, float] = field(default_factory=dict)
    effects: Dict[str, float] = field(default_factory=dict)
    discovered: bool = False
    discovery_time: float = 0.0
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent technologies
    capabilities: Dict[str, Any] = field(default_factory=dict)  # Technology capabilities
    requirements: Dict[str, Any] = field(default_factory=dict)  # Technology requirements
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Innovation:
    type: str  # Emergent innovation type
    name: str
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent innovations
    conditions: Dict[str, Any] = field(default_factory=dict)  # Innovation conditions
    effects: Dict[str, Any] = field(default_factory=dict)  # Innovation effects
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

@dataclass
class TechnologicalEvolution:
    type: str  # Emergent evolution type
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent evolution
    conditions: Dict[str, Any] = field(default_factory=dict)  # Evolution conditions
    effects: Dict[str, Any] = field(default_factory=dict)  # Evolution effects
    created_at: float = field(default_factory=time.time)

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
            prerequisites={"basic_tools", "fire"},
            difficulty=0.3,
            discovery_chance=0.005,
            required_resources={"land": 1.0, "water": 1.0},
            effects={"food_production": 2.0, "population_growth": 1.5}
        )
        
        self.technologies["irrigation"] = Technology(
            name="Irrigation",
            category=TechnologyCategory.AGRICULTURE,
            description="Methods for watering crops",
            prerequisites={"basic_farming"},
            difficulty=0.4,
            discovery_chance=0.001,
            required_resources={"land": 1.0},
            effects={"food_production": 1.5, "water_efficiency": 1.3}
        )
        
        # Tools technologies
        self.technologies["basic_tools"] = Technology(
            name="Basic Tools",
            category=TechnologyCategory.TOOLS,
            description="Simple tools for gathering and processing resources",
            prerequisites={},
            difficulty=0.1,
            discovery_chance=0.05,
            required_resources={"stone": 1.0},
            effects={"gathering_efficiency": 1.5}
        )
        
        self.technologies["advanced_tools"] = Technology(
            name="Advanced Tools",
            category=TechnologyCategory.TOOLS,
            description="More sophisticated tools for better resource processing",
            prerequisites={"basic_tools"},
            difficulty=0.2,
            discovery_chance=0.01,
            required_resources={"copper": 1.0},
            effects={"gathering_efficiency": 1.8}
        )
        
        # Shelter technologies
        self.technologies["basic_shelter"] = Technology(
            name="Basic Shelter",
            category=TechnologyCategory.SHELTER,
            description="Simple structures for protection from elements",
            prerequisites={"basic_tools"},
            difficulty=0.2,
            discovery_chance=0.01,
            required_resources={"wood": 1.0},
            effects={"shelter_quality": 1.2}
        )
        
        # Medicine technologies
        self.technologies["basic_medicine"] = Technology(
            name="Basic Medicine",
            category=TechnologyCategory.MEDICINE,
            description="Understanding of basic healing and disease prevention",
            prerequisites={"fire"},
            difficulty=0.2,
            discovery_chance=0.01,
            required_resources={"herbs": 1.0},
            effects={"health_recovery": 1.5, "disease_resistance": 1.5}
        )
        
        # Weapons technologies
        self.technologies["basic_weapons"] = Technology(
            name="Basic Weapons",
            category=TechnologyCategory.WEAPONS,
            description="Simple weapons for hunting and defense",
            prerequisites={"basic_tools"},
            difficulty=0.2,
            discovery_chance=0.01,
            required_resources={"stone": 1.0},
            effects={"hunting_efficiency": 1.2, "combat_strength": 1.2}
        )
        
        # Clothing technologies
        self.technologies["basic_clothing"] = Technology(
            name="Basic Clothing",
            category=TechnologyCategory.CLOTHING,
            description="Simple clothing for protection from elements",
            prerequisites={"basic_tools"},
            difficulty=0.2,
            discovery_chance=0.01,
            required_resources={"cloth": 1.0},
            effects={"temperature_resistance": 1.2}
        )
        
        # Transportation technologies
        self.technologies["basic_transportation"] = Technology(
            name="Basic Transportation",
            category=TechnologyCategory.TRANSPORTATION,
            description="Simple methods for moving goods and people",
            prerequisites={"basic_tools"},
            difficulty=0.2,
            discovery_chance=0.01,
            required_resources={"wood": 1.0},
            effects={"transport_efficiency": 1.2, "carrying_capacity": 1.2}
        )
        
        # Communication technologies
        self.technologies["basic_communication"] = Technology(
            name="Basic Communication",
            category=TechnologyCategory.COMMUNICATION,
            description="Simple methods for sharing information",
            prerequisites={"basic_shelter"},
            difficulty=0.3,
            discovery_chance=0.001,
            required_resources={"clay": 1.0},
            effects={"communication_range": 2.0}
        )
        
        # Culture technologies
        self.technologies["basic_culture"] = Technology(
            name="Basic Culture",
            category=TechnologyCategory.CULTURE,
            description="Simple forms of artistic and cultural expression",
            prerequisites={"basic_shelter"},
            difficulty=0.3,
            discovery_chance=0.001,
            required_resources={"clay": 1.0},
            effects={"happiness": 1.1, "social_cohesion": 1.1}
        )
        
        # Governance technologies
        self.technologies["basic_governance"] = Technology(
            name="Basic Governance",
            category=TechnologyCategory.GOVERNANCE,
            description="Simple methods for organizing society",
            prerequisites={"basic_shelter"},
            difficulty=0.3,
            discovery_chance=0.001,
            required_resources={"clay": 1.0},
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
        current_tech.discovery_time = time.time()
        current_tech.discovered = True
        self.discovered_technologies.add(current_tech.name)
        newly_discovered.append(current_tech.name)
        self.research_queue.pop(0)
        logger.info(f"Discovered new technology: {current_tech.name}")
        
        self._apply_technology_effects(current_tech)
        
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
        return self.technologies[technology_name].discovery_time

    def to_dict(self) -> Dict:
        """Convert technology tree state to dictionary for serialization."""
        return {
            "technologies": {
                name: {
                    "name": tech.name,
                    "category": tech.category.value,
                    "description": tech.description,
                    "prerequisites": list(tech.prerequisites),
                    "difficulty": tech.difficulty,
                    "discovery_chance": tech.discovery_chance,
                    "required_resources": tech.required_resources,
                    "effects": tech.effects,
                    "discovered": tech.discovered,
                    "discovery_time": tech.discovery_time
                }
                for name, tech in self.technologies.items()
            },
            "discovered_technologies": list(self.discovered_technologies),
            "research_queue": self.research_queue
        }

class TechnologySystem:
    def __init__(self, world):
        self.world = world
        self.technology_tree = TechnologyTree()
        self.innovations = {}
        self.evolutions = {}
        self.discovery_chance = 0.01
        self.research_points = 0.0
        self.last_update = time.time()
        
    def initialize_technology(self):
        """Initialize the technology system."""
        logger.info("Initializing technology system...")
        
        # Initialize basic technologies
        logger.info("Setting up basic technologies...")
        self.technology_tree._initialize_technologies()
        
        # Initialize research queue
        logger.info("Initializing research queue...")
        self.technology_tree.research_queue = []
        
        # Initialize discovery tracking
        logger.info("Initializing discovery tracking...")
        self.discovery_chance = 0.01
        self.research_points = 0.0
        
        # Verify initialization
        if not self.verify_initialization():
            logger.error("Technology system initialization verification failed")
            raise RuntimeError("Technology system initialization verification failed")
            
        logger.info("Technology system initialization complete")

    def verify_initialization(self) -> bool:
        """Verify that the technology system is properly initialized."""
        logger.info("Verifying technology system initialization...")
        
        # Check technology tree
        if not hasattr(self, 'technology_tree') or not self.technology_tree:
            logger.error("Technology tree not initialized")
            return False
            
        # Check innovations
        if not hasattr(self, 'innovations'):
            logger.error("Innovations not initialized")
            return False
            
        # Check evolutions
        if not hasattr(self, 'evolutions'):
            logger.error("Evolutions not initialized")
            return False
            
        # Check research queue
        if not hasattr(self.technology_tree, 'research_queue'):
            logger.error("Research queue not initialized")
            return False
            
        # Check discovery tracking
        if not hasattr(self, 'discovery_chance') or not hasattr(self, 'research_points'):
            logger.error("Discovery tracking not initialized")
            return False
            
        # Check required technology types
        required_types = {'agriculture', 'construction', 'transportation', 'communication', 'medicine'}
        if not all(tech_type in self.technology_tree.technologies for tech_type in required_types):
            logger.error("Not all required technology types initialized")
            return False
            
        logger.info("Technology system initialization verified successfully")
        return True

    def get_state(self) -> Dict:
        """Get current technology state."""
        return {
            "technology_tree": self.technology_tree.to_dict(),
            "innovations": {id: innovation.to_dict() for id, innovation in self.innovations.items()},
            "evolutions": {id: evolution.to_dict() for id, evolution in self.evolutions.items()},
            "discovery_chance": self.discovery_chance,
            "research_points": self.research_points
        }
        
    def load_state(self, state: Dict):
        """Load technology system state."""
        self.technology_tree = TechnologyTree()
        self.technology_tree.technologies = state.get("technology_tree", {}).get("technologies", {})
        self.technology_tree.discovered_technologies = set(state.get("technology_tree", {}).get("discovered_technologies", []))
        self.technology_tree.research_queue = state.get("technology_tree", {}).get("research_queue", [])
        self.innovations = state.get("innovations", {})
        self.evolutions = state.get("evolutions", {})
        self.discovery_chance = state.get("discovery_chance", 0.01)
        self.research_points = state.get("research_points", 0.0)
        self.last_update = state.get("last_update", time.time())
        
    def update(self, time_delta: float):
        """Update technology system state."""
        # Check for potential discoveries based on agent actions and environment
        self._check_for_discoveries()
        
    def _check_for_discoveries(self):
        """Check for new technology discoveries based on agent actions and observations."""
        for agent in self.world.agents.values():
            # Check agent's recent actions and observations
            for action in agent.recent_actions:
                # Check for stone tool discovery
                if action["type"] == "use_rock" and action.get("purpose") == "cut":
                    self.attempt_discovery("stone_tools", agent)
                    
                # Check for fire discovery
                elif action["type"] == "drop_stone" and action.get("context") == "near_dry_grass":
                    self.attempt_discovery("fire", agent)
                    
                # Check for shelter discovery
                elif action["type"] == "build" and action.get("material") == "wood":
                    self.attempt_discovery("shelter", agent)
                    
            # Check for novel discoveries based on unique experiences
            self._check_for_novel_discoveries(agent)
            
    def _check_for_novel_discoveries(self, agent):
        """Check for novel, unexpected discoveries based on agent experiences."""
        # Calculate novelty score based on agent's unique experiences
        novelty_score = self._calculate_novelty_score(agent)
        
        # If novelty score is high enough, attempt to generate a novel technology
        if novelty_score > 0.7:  # High threshold for novel discoveries
            self._generate_novel_technology(agent, novelty_score)
            
    def _calculate_novelty_score(self, agent):
        """Calculate how novel an agent's experiences are."""
        score = 0.0
        
        # Consider agent's traits
        if hasattr(agent, 'genes'):
            score += agent.genes.get('curiosity', 0.5) * 0.3
            score += agent.genes.get('intelligence', 0.5) * 0.3
            
        # Consider unique combinations of actions
        unique_combinations = set()
        for i, action1 in enumerate(agent.recent_actions):
            for action2 in agent.recent_actions[i+1:]:
                combo = (action1["type"], action2["type"])
                if combo not in unique_combinations:
                    unique_combinations.add(combo)
                    score += 0.1
                    
        # Consider environmental context
        if hasattr(agent, 'position'):
            terrain = self.world.get_terrain_at(*agent.position)
            weather = self.world.get_weather_at(*agent.position)
            if terrain and weather:
                score += 0.2  # Bonus for environmental awareness
                
        return min(score, 1.0)  # Cap at 1.0
        
    def _generate_novel_technology(self, agent, novelty_score):
        """Generate a novel technology based on agent's experiences."""
        # Generate technology type based on agent's experiences
        tech_type = self._generate_tech_type(agent)
        
        # Generate unique name and description
        name = self._generate_tech_name(tech_type)
        description = self._generate_tech_description(tech_type, agent)
        
        # Create new technology
        tech_id = f"tech_{len(self.technology_tree.technologies)}"
        new_tech = Technology(
            id=tech_id,
            name=name,
            description=description,
            type=tech_type,
            prerequisites=set(),  # Novel technologies might not have prerequisites
            discovered=False
        )
        
        # Add to technologies
        self.technology_tree.technologies[tech_id] = new_tech
        
        # Mark as discovered
        new_tech.discovered = True
        
        # Log the discovery
        self.discoveries.append({
            "technology": tech_id,
            "discoverer": agent.id,
            "timestamp": datetime.now().isoformat(),
            "novelty_score": novelty_score
        })
        
        logger.info(f"Novel technology discovered: {name} by agent {agent.id}")
        
    def _generate_tech_type(self, agent):
        """Generate a technology type based on agent's experiences."""
        # Analyze agent's recent actions and observations
        action_types = set(action["type"] for action in agent.recent_actions)
        
        # Map action combinations to technology types
        if {"use_rock", "use_wood"} <= action_types:
            return "primitive_tools"
        elif {"observe_fire", "use_wood"} <= action_types:
            return "fire_control"
        elif {"build", "use_wood"} <= action_types:
            return "shelter"
        else:
            return "unknown"
            
    def _generate_tech_name(self, tech_type):
        """Generate a name for a technology based on its type."""
        prefixes = ["primitive", "basic", "simple", "early"]
        suffixes = ["tool", "device", "method", "technique"]
        
        if tech_type == "primitive_tools":
            return f"{random.choice(prefixes)} {random.choice(suffixes)}"
        elif tech_type == "fire_control":
            return "fire making"
        elif tech_type == "shelter":
            return "basic shelter"
        else:
            return f"unknown {random.choice(suffixes)}"
            
    def _generate_tech_description(self, tech_type, agent):
        """Generate a description for a technology based on its type and discoverer."""
        if tech_type == "primitive_tools":
            return f"A {agent.name}'s discovery of using natural materials as tools"
        elif tech_type == "fire_control":
            return f"{agent.name}'s method of creating and controlling fire"
        elif tech_type == "shelter":
            return f"{agent.name}'s technique for building protective structures"
        else:
            return "An unexpected discovery with unknown applications"

    def create_technology(self, type: str, name: str, description: str,
                         properties: Dict[str, Any] = None) -> Technology:
        """Create new technology with custom properties."""
        technology = Technology(
            type=type,
            name=name,
            description=description,
            properties=properties or {}
        )
        
        technology_id = f"technology_{len(self.technology_tree.technologies)}"
        self.technology_tree.technologies[technology_id] = technology
        logger.info(f"Created new technology: {name} of type {type}")
        return technology
        
    def create_innovation(self, type: str, name: str, description: str,
                         properties: Dict[str, Any] = None) -> Innovation:
        """Create new innovation with custom properties."""
        innovation = Innovation(
            type=type,
            name=name,
            description=description,
            properties=properties or {}
        )
        
        innovation_id = f"innovation_{len(self.innovations)}"
        self.innovations[innovation_id] = innovation
        logger.info(f"Created new innovation: {name} of type {type}")
        return innovation
        
    def create_evolution(self, type: str, description: str,
                        properties: Dict[str, Any] = None,
                        conditions: Dict[str, Any] = None,
                        effects: Dict[str, Any] = None) -> TechnologicalEvolution:
        """Create new technological evolution with custom properties."""
        evolution = TechnologicalEvolution(
            type=type,
            description=description,
            properties=properties or {},
            conditions=conditions or {},
            effects=effects or {}
        )
        
        evolution_id = f"evolution_{len(self.evolutions)}"
        self.evolutions[evolution_id] = evolution
        logger.info(f"Created new technological evolution of type {type}")
        return evolution
        
    def add_capability_to_technology(self, technology: str, capability: Dict[str, Any]) -> bool:
        """Add capability to a technology."""
        if technology not in self.technology_tree.technologies:
            logger.error(f"Technology {technology} does not exist")
            return False
            
        self.technology_tree.technologies[technology].capabilities.update(capability)
        logger.info(f"Added capability to technology {technology}")
        return True
        
    def to_dict(self) -> Dict:
        """Convert technology system state to dictionary for serialization."""
        return {
            "technology_tree": self.technology_tree.to_dict(),
            "innovations": self.innovations,
            "evolutions": self.evolutions,
            "discoveries": self.discoveries
        }

    def attempt_discovery(self, tech_type: str, agent):
        """Attempt to discover a new technology based on agent's recent actions and observations."""
        # Check if the technology is already discovered
        if tech_type in self.technology_tree.technologies and self.technology_tree.technologies[tech_type].discovered:
            logger.warning(f"Technology {tech_type} already discovered")
            return
            
        # Check if the technology is in the research queue
        if tech_type in self.technology_tree.technologies and tech_type in self.technology_tree.research_queue:
            logger.warning(f"Technology {tech_type} already in research queue")
            return
            
        # Check if the technology is in the available technologies list
        if tech_type in self.technology_tree.technologies and self.technology_tree.technologies[tech_type] in self.technology_tree.get_available_technologies():
            logger.warning(f"Technology {tech_type} already available for research")
            return
            
        # Check if the technology is in the discovered technologies set
        if tech_type in self.technology_tree.technologies and tech_type in self.technology_tree.discovered_technologies:
            logger.warning(f"Technology {tech_type} already discovered")
            return
            
        # Check if the technology is in the technology tree
        if tech_type in self.technology_tree.technologies:
            logger.warning(f"Technology {tech_type} already exists in technology tree")
            return
            
        # Check if the technology is in the world
        if tech_type not in self.world.technologies:
            logger.warning(f"Technology {tech_type} not found in the world")
            return
            
        # Check if the technology is in the agent's discovered concepts
        if tech_type not in agent.discovered_concepts:
            logger.warning(f"Technology {tech_type} not discovered by agent {agent.id}")
            return
            
        # Check if the technology is in the agent's recent actions
        if tech_type not in [action["type"] for action in agent.recent_actions]:
            logger.warning(f"Technology {tech_type} not found in agent {agent.id}'s recent actions")
            return
            
        # Check if the technology is in the agent's recent observations
        if tech_type not in [observation["type"] for observation in agent.recent_observations]:
            logger.warning(f"Technology {tech_type} not found in agent {agent.id}'s recent observations")
            return
            
        # Check if the technology is in the world's technology categories
        if tech_type not in self.world.technology_categories:
            logger.warning(f"Technology {tech_type} not found in the world's technology categories")
            return
            
        # Check if the technology is in the world's technology requirements
        if tech_type not in self.world.technology_requirements:
            logger.warning(f"Technology {tech_type} not found in the world's technology requirements")
            return
            
        # Check if the technology is in the world's technology effects
        if tech_type not in self.world.technology_effects:
            logger.warning(f"Technology {tech_type} not found in the world's technology effects")
            return
            
        # Check if the technology is in the world's technology properties
        if tech_type not in self.world.technology_properties:
            logger.warning(f"Technology {tech_type} not found in the world's technology properties")
            return
            
        # Check if the technology is in the world's technology capabilities
        if tech_type not in self.world.technology_capabilities:
            logger.warning(f"Technology {tech_type} not found in the world's technology capabilities")
            return
            
        # If all checks pass, create the technology
        tech = self.create_technology(
            type=tech_type,
            name=tech_type.replace("_", " ").title(),
            description=f"Discovered by {agent.name}",
            properties={
                "discovered_by": agent.id,
                "discovery_context": {
                    "actions": agent.recent_actions,
                    "observations": agent.recent_observations
                }
            }
        )
        
        # Add to agent's discovered concepts
        agent.discovered_concepts.add(tech_type)
        
        # Log the discovery
        self.discoveries.append({
            "type": "technology",
            "name": tech_type,
            "agent_id": agent.id,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Agent {agent.id} discovered {tech_type}!")

    def _check_for_novel_discoveries(self, agent_id: str, actions: List[Dict], observations: List[Dict]):
        """Check for completely novel, unexpected discoveries based on unique agent experiences."""
        agent = self.world.agents[agent_id]
        
        # Get unique combinations of actions and observations
        unique_experiences = self._get_unique_experiences(actions, observations)
        
        for experience in unique_experiences:
            # Calculate novelty score based on:
            # 1. How unique this combination is
            # 2. Agent's creativity and intelligence
            # 3. Environmental context
            novelty_score = self._calculate_novelty_score(agent, experience)
            
            # If novelty score is high enough, attempt a novel discovery
            if novelty_score > 0.8:  # 80% threshold for novel discoveries
                self._attempt_novel_discovery(agent_id, experience)
                
    def _get_unique_experiences(self, actions: List[Dict], observations: List[Dict]) -> List[Dict]:
        """Get unique combinations of actions and observations that might lead to novel discoveries."""
        unique_experiences = []
        
        # Look for interesting combinations
        for action in actions:
            for observation in observations:
                # Check if this combination is unique and interesting
                if self._is_interesting_combination(action, observation):
                    unique_experiences.append({
                        'action': action,
                        'observation': observation,
                        'context': self._get_combined_context(action, observation)
                    })
                    
        return unique_experiences
        
    def _is_interesting_combination(self, action: Dict, observation: Dict) -> bool:
        """Check if a combination of action and observation is interesting enough for potential discovery."""
        # Look for unusual or unexpected combinations
        action_type = action.get('type')
        observation_type = observation.get('type')
        
        # Example interesting combinations:
        interesting_combos = [
            ('use', 'weather_change'),  # Using something during weather change
            ('build', 'animal_behavior'),  # Building while observing animals
            ('experiment', 'unexpected_result'),  # Experimenting with unexpected results
            ('combine', 'chemical_reaction'),  # Combining things with chemical reactions
            ('modify', 'structural_change')  # Modifying something with structural changes
        ]
        
        return (action_type, observation_type) in interesting_combos
        
    def _calculate_novelty_score(self, agent, experience: Dict) -> float:
        """Calculate how likely this experience is to lead to a novel discovery."""
        base_score = 0.5
        
        # Add agent's creativity and intelligence
        agent_traits = (
            agent.genes.get('creativity', 0.5) +
            agent.genes.get('intelligence', 0.5) +
            agent.genes.get('curiosity', 0.5)
        ) / 3.0
        
        # Add environmental context
        context_score = self._get_context_novelty(experience['context'])
        
        # Add randomness for unexpected discoveries
        random_factor = random.random() * 0.3
        
        return min(1.0, base_score + agent_traits * 0.3 + context_score * 0.2 + random_factor)
        
    def _get_context_novelty(self, context: Dict) -> float:
        """Calculate how novel the current context is."""
        novelty_factors = {
            'weather_change': 0.2,
            'unexpected_result': 0.3,
            'chemical_reaction': 0.25,
            'structural_change': 0.15,
            'animal_behavior': 0.1
        }
        
        return sum(novelty_factors.get(factor, 0) for factor in context.get('factors', []))
        
    def _attempt_novel_discovery(self, agent_id: str, experience: Dict):
        """Attempt to make a completely novel discovery based on unique experience."""
        agent = self.world.agents[agent_id]
        
        # Generate a novel technology based on the experience
        tech_type = self._generate_novel_tech_type(experience)
        tech_name = self._generate_novel_tech_name(tech_type, experience)
        tech_description = self._generate_novel_tech_description(tech_type, experience)
        
        # Create the novel technology
        tech = self.create_technology(
            type=tech_type,
            name=tech_name,
            description=tech_description,
            properties={
                'discovered_by': agent_id,
                'discovery_context': experience,
                'is_novel': True,
                'prerequisites': self._get_novel_prerequisites(experience)
            }
        )
        
        # Add to agent's discovered concepts
        agent.discovered_concepts.add(tech_type)
        
        # Log the novel discovery
        self.discoveries.append({
            'type': 'novel_technology',
            'name': tech_name,
            'agent_id': agent_id,
            'context': experience,
            'timestamp': time.time()
        })
        
        self.logger.info(f"Agent {agent_id} made a novel discovery: {tech_name}!")
        
    def _generate_novel_tech_type(self, experience: Dict) -> str:
        """Generate a novel technology type based on the experience."""
        # Combine elements from the experience to create a novel type
        action_type = experience['action'].get('type', '')
        observation_type = experience['observation'].get('type', '')
        
        # Create a unique type identifier
        return f"novel_{action_type}_{observation_type}_{int(time.time())}"
        
    def _generate_novel_tech_name(self, tech_type: str, experience: Dict) -> str:
        """Generate a name for the novel technology."""
        # Use elements from the experience to create a descriptive name
        action = experience['action'].get('type', '')
        observation = experience['observation'].get('type', '')
        context = experience['context'].get('factors', [])
        
        # Create a descriptive name
        return f"Novel {action.title()} {observation.title()} Technology"
        
    def _generate_novel_tech_description(self, tech_type: str, experience: Dict) -> str:
        """Generate a description for the novel technology."""
        # Create a description based on how it was discovered
        action = experience['action']
        observation = experience['observation']
        
        return f"A novel technology discovered through {action.get('type')} " \
               f"while observing {observation.get('type')}. " \
               f"This discovery emerged from unique circumstances " \
               f"and represents a new approach to {action.get('purpose', 'problem-solving')}."
               
    def _get_novel_prerequisites(self, experience: Dict) -> List[str]:
        """Get prerequisites for the novel technology."""
        # Novel technologies might have unique prerequisites
        return [
            f"understanding_of_{experience['action'].get('type')}",
            f"knowledge_of_{experience['observation'].get('type')}"
        ] 