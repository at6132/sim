from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Any
import random
from datetime import datetime
import uuid
import logging
from .philosophy import Philosophy
from .emotions import EmotionSystem, EmotionType
from .cognition import CognitiveSystem, ThoughtType, Thought
from .life_cycle import LifeCycleSystem, LifeStage, PregnancyStage
from .animals import Animal, AnimalType, AnimalTemperament
from enum import Enum
import time
from .environment import Environment
from .weather import WeatherType
from .terrain import TerrainType
from .resources import ResourceType
import math
from .genes import Genes  # Import Genes from genes.py
from .needs import AgentNeeds
from .memory import Memory
from .moral_alignment import MoralAlignment
from .social_state import SocialState
from .crisis_state import CrisisState
from .identification import IdentificationSystem
from .utils.logging_config import get_logger
from .cooking import FoodType

# Initialize logger
logger = get_logger(__name__)

@dataclass
class Relationship:
    compatibility: float = 0.5  # 0-1 scale
    attraction: float = 0.5     # 0-1 scale
    trust: float = 0.5         # 0-1 scale
    affection: float = 0.5     # 0-1 scale
    last_interaction: float = 0.0
    shared_interests: float = 0.5  # 0-1 scale
    relationship_type: str = "neutral"  # friend, enemy, mate, etc.
    interaction_history: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert relationship to dictionary for serialization."""
        return {
            "compatibility": self.compatibility,
            "attraction": self.attraction,
            "trust": self.trust,
            "affection": self.affection,
            "last_interaction": self.last_interaction,
            "shared_interests": self.shared_interests,
            "relationship_type": self.relationship_type,
            "interaction_history": self.interaction_history
        }

@dataclass
class Resource:
    type: ResourceType
    amount: float
    longitude: float
    latitude: float
    quality: float = 1.0
    last_harvested: float = 0.0
    regeneration_rate: float = 0.1

    def to_dict(self) -> Dict:
        """Convert resource to dictionary for serialization."""
        return {
            "type": self.type.value,
            "amount": self.amount,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "quality": self.quality,
            "last_harvested": self.last_harvested,
            "regeneration_rate": self.regeneration_rate
        }

@dataclass
class Memory:
    event: str
    importance: float
    timestamp: datetime
    context: Dict
    concepts: Set[str]  # Concepts discovered/learned from this memory
    animal_interactions: List[Dict]  # Track interactions with animals
    domesticated_animals: List[str]  # IDs of animals owned by this agent
    emotional_impact: float = 0.0  # How emotionally significant this memory is
    philosophical_impact: float = 0.0  # How philosophically significant this memory is
    cognitive_impact: float = 0.0  # How significant this memory is for thinking

    def to_dict(self) -> Dict:
        """Convert memory to dictionary for serialization."""
        return {
            "event": self.event,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "concepts": list(self.concepts),
            "animal_interactions": self.animal_interactions,
            "domesticated_animals": self.domesticated_animals,
            "emotional_impact": self.emotional_impact,
            "philosophical_impact": self.philosophical_impact,
            "cognitive_impact": self.cognitive_impact
        }

@dataclass
class Genes:
    curiosity: float  # 0-1 scale
    strength: float
    intelligence: float
    social_drive: float
    creativity: float
    adaptability: float
    philosophical_tendency: float  # How likely to ponder deep questions
    emotional_depth: float  # How deeply they experience emotions
    existential_awareness: float  # How likely to question existence
    cognitive_complexity: float  # How complex their thoughts can be
    cultural_sensitivity: float  # How attuned they are to cultural aspects
    fertility: float  # How likely to conceive
    longevity: float  # How long they live
    disease_resistance: float  # How resistant to disease
    metabolism: float  # How efficiently they process food
    animal_affinity: float  # Natural ability to work with animals
    hunting_skill: float    # Ability to hunt animals
    taming_skill: float     # Ability to tame animals
    
    # Physical attractiveness traits
    facial_symmetry: float = 0.5  # Symmetry of facial features (0-1)
    body_proportion: float = 0.5  # Overall body proportions (0-1)
    skin_quality: float = 0.5     # Skin health and appearance (0-1)
    hair_quality: float = 0.5     # Hair health and appearance (0-1)
    height: float = 0.5          # Height relative to population average (0-1)
    muscle_tone: float = 0.5     # Muscle definition and tone (0-1)
    voice_quality: float = 0.5   # Voice attractiveness (0-1)
    eye_color: float = 0.5       # Eye color attractiveness (0-1)
    hair_color: float = 0.5      # Hair color attractiveness (0-1)
    
    # Evolutionary physical traits
    eye_shape: float = 0.5  # 0 = narrow (Asian), 1 = wide (European)
    skin_pigment: float = 0.5  # 0 = dark, 1 = light
    nose_shape: float = 0.5  # 0 = narrow, 1 = wide
    body_hair: float = 0.5  # 0 = sparse, 1 = dense
    body_fat_distribution: float = 0.5  # 0 = even, 1 = concentrated
    muscle_mass: float = 0.5  # 0 = lean, 1 = muscular
    bone_density: float = 0.5  # 0 = light, 1 = dense
    cold_resistance: float = 0.5  # 0 = low, 1 = high
    heat_resistance: float = 0.5  # 0 = low, 1 = high
    uv_resistance: float = 0.5  # 0 = low, 1 = high
    
    # Environmental adaptation traits
    altitude_tolerance: float = 0.5  # Ability to handle high altitudes
    oxygen_efficiency: float = 0.5  # Efficiency of oxygen usage
    humidity_tolerance: float = 0.5  # Ability to handle humidity
    drought_resistance: float = 0.5  # Ability to handle dry conditions
    swimming_ability: float = 0.5  # Natural swimming ability
    breath_holding: float = 0.5  # Ability to hold breath
    stealth: float = 0.5  # Natural stealth ability
    climbing_ability: float = 0.5  # Natural climbing ability
    water_resistance: float = 0.5  # Ability to handle wet conditions
    dust_resistance: float = 0.5  # Ability to handle dusty conditions
    agility: float = 0.5  # Overall agility
    
    def calculate_attractiveness(self, cultural_preferences: Dict[str, float] = None) -> float:
        """Calculate overall attractiveness based on physical traits and cultural preferences."""
        if cultural_preferences is None:
            cultural_preferences = {
                "facial_symmetry": 0.8,
                "body_proportion": 0.7,
                "skin_quality": 0.6,
                "hair_quality": 0.5,
                "height": 0.4,
                "muscle_tone": 0.3,
                "voice_quality": 0.4,
                "eye_color": 0.3,
                "hair_color": 0.3
            }
            
        # Calculate weighted average of physical traits
        total_weight = sum(cultural_preferences.values())
        attractiveness = sum(
            getattr(self, trait) * weight 
            for trait, weight in cultural_preferences.items()
        ) / total_weight
        
        return attractiveness

@dataclass
class AgentNeeds:
    hunger: float = 1.0  # 0-1 scale, 1.0 is full
    thirst: float = 1.0
    energy: float = 1.0
    health: float = 1.0
    bladder: float = 0.0  # 0-1 scale, 1.0 is urgent
    bowel: float = 0.0   # 0-1 scale, 1.0 is urgent
    hygiene: float = 1.0  # 0-1 scale, 1.0 is clean
    comfort: float = 1.0
    social: float = 0.5
    safety: float = 1.0
    reproduction_urge: float = 0.0
    animal_companionship: float = 0.5  # Need for animal companionship
    hunting_urge: float = 0.5  # Urge to hunt animals
    emotional_expression: float = 0.5  # Need to express emotions
    purpose: float = 0.5  # Need for purpose/meaning
    understanding: float = 0.5  # Need for understanding
    philosophical_expression: float = 0.5  # Need for philosophical expression
    creative_expression: float = 0.5  # Need for creative expression
    reproduction: float = 0.0  # Need for reproduction
    rest: float = 1.0  # Need for rest/sleep

@dataclass
class MoralAlignment(Enum):
    LAWFUL_GOOD = "lawful_good"
    NEUTRAL_GOOD = "neutral_good"
    CHAOTIC_GOOD = "chaotic_good"
    LAWFUL_NEUTRAL = "lawful_neutral"
    TRUE_NEUTRAL = "true_neutral"
    CHAOTIC_NEUTRAL = "chaotic_neutral"
    LAWFUL_EVIL = "lawful_evil"
    NEUTRAL_EVIL = "neutral_evil"
    CHAOTIC_EVIL = "chaotic_evil"

@dataclass
class CrisisState:
    is_crisis: bool = False
    crisis_severity: float = 0.0  # 0-100
    crisis_type: str = "none"  # famine, war, plague, etc.
    moral_compromise: float = 0.0  # 0-100, how much they've compromised their morals
    last_crime_time: float = 0.0
    crime_cooldown: float = 0.0
    survival_instinct: float = 50.0  # 0-100, affects willingness to commit crimes
    paranoia: float = 0.0  # 0-100, affects trust in others

@dataclass
class SocialState:
    is_lawful: bool = False  # Whether they believe in laws
    law_preference: float = 0.0  # 0-100, how much they prefer laws vs anarchy
    violence_tolerance: float = 50.0  # 0-100, how much they tolerate violence
    power_seeking: float = 50.0  # 0-100, desire for power/control
    has_established_laws: bool = False  # Whether they've created laws in their tribe
    laws: Dict[str, Dict] = field(default_factory=dict)  # Any laws they've created
    crimes_committed: List[Dict] = field(default_factory=list)  # Detailed crime history

@dataclass
class Agent:
    id: str
    name: str = ""  # Empty by default, will be developed through interactions
    age: float = 0
    gender: str = "unknown"
    genes: Genes = field(default_factory=Genes)  # Use Genes from genes.py
    needs: AgentNeeds = field(default_factory=AgentNeeds)
    memory: Memory = field(default_factory=Memory)
    emotions: EmotionSystem = field(default_factory=EmotionSystem)
    health: float = 1.0
    philosophy: Philosophy = field(default_factory=Philosophy)
    longitude: float = 0.0
    latitude: float = 0.0
    inventory: Dict[str, float] = field(default_factory=dict)
    skills: Dict[str, float] = field(default_factory=dict)
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    tribe_id: Optional[str] = None
    settlement_id: Optional[str] = None
    last_action: str = "idle"
    last_action_time: float = 0.0
    identification: IdentificationSystem = field(default_factory=lambda: None)
    known_identifiers: Dict[str, str] = field(default_factory=dict)

    def __init__(self, id: str, name: str = "", age: float = 0, gender: str = "unknown",
                 genes: Optional[Genes] = None, needs: Optional[AgentNeeds] = None,
                 memory: Optional[Memory] = None, emotions: Optional[EmotionSystem] = None,
                 health: float = 1.0, philosophy: Optional[Philosophy] = None,
                 longitude: float = 0.0, latitude: float = 0.0):
        self.id = id
        self.name = name  # Empty by default
        self.age = age
        self.gender = gender
        self.genes = genes or Genes()  # Use Genes from genes.py
        self.needs = needs or AgentNeeds()
        self.memory = memory or Memory()
        self.emotions = emotions or EmotionSystem()
        self.health = health
        self.philosophy = philosophy or Philosophy()
        self.longitude = longitude
        self.latitude = latitude
        self.inventory = {}
        self.skills = {}
        self.relationships = {}
        self.tribe_id = None
        self.settlement_id = None
        self.last_action = "idle"
        self.last_action_time = 0.0
        self.identification = IdentificationSystem(agent_id=id)
        self.known_identifiers = {}

    def update(self, time_delta: float, world_state: Dict):
        """Update agent state."""
        # Update identification system
        self.identification.update_identifiers(world_state)
        
        # Update known identifiers from interactions
        nearby_agents = world_state.get("agents", {})
        for agent_id, agent in nearby_agents.items():
            if agent_id != self.id:
                identifier = agent.identification.get_identifier(self.id)
                if identifier:
                    self.known_identifiers[agent_id] = identifier

        # Continue with existing update logic
        self.age += time_delta / (365 * 24 * 3600)  # Convert seconds to years
        self.needs.update(time_delta)
        self.health.update(time_delta, world_state)
        self.emotions.update(time_delta, world_state)
        self.relationships.update(time_delta, world_state)
        self.cognition.update(time_delta, world_state)
        self.philosophy.update(time_delta, world_state)

    def get_identifier_for(self, target_id: str) -> str:
        """Get how this agent identifies another agent."""
        return self.identification.get_identifier(target_id) or "unknown"

    def get_known_identifier(self) -> str:
        """Get how other agents identify this agent."""
        if self.known_identifiers:
            # Return the most common identifier
            identifiers = list(self.known_identifiers.values())
            return max(set(identifiers), key=identifiers.count)
        return "unknown"

    def to_dict(self) -> dict:
        """Serialize agent state for frontend or saving."""
        return {
            'id': self.id,
            'name': self.name,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'health': self.health,
            'age': self.age,
            'gender': self.gender,
            'inventory': self.inventory,
            'skills': self.skills,
            'tribe_id': self.tribe_id,
            'settlement_id': self.settlement_id,
            'last_action': self.last_action,
            'last_action_time': self.last_action_time,
        }

    def is_alive(self) -> bool:
        """Check if the agent is alive."""
        return not self.is_dead and self.health > 0
        
    def die(self) -> None:
        """Mark the agent as dead."""
        self.is_dead = True
        self.health = 0
        self.needs = None  # Clear needs when dead
        self.emotions = None  # Clear emotions when dead
        self.philosophy = None  # Clear philosophy when dead
        
    def evolve_for_environment(self, environment: Environment) -> None:
        """Evolve genes based on environmental conditions."""
        # Get climate data at agent's position
        climate = environment.get_climate_at(self.position[0], self.position[1])
        temperature = climate["temperature"]  # Celsius
        humidity = climate["humidity"]  # 0-1 scale
        uv_level = climate["uv_level"]  # 0-1 scale
        elevation = climate["elevation"]  # meters
        
        # Get terrain data
        terrain = environment.get_terrain_at(self.position[0], self.position[1])
        terrain_type = terrain.type if terrain else None
        
        # Get weather data
        weather = environment.get_weather_at(self.position[0], self.position[1])
        weather_type = weather["type"]
        weather_intensity = weather["intensity"]
        
        # Temperature adaptations
        if temperature > 30:  # Hot environment
            self.genes.heat_resistance += 0.01
            self.genes.cold_resistance -= 0.005
        elif temperature < 10:  # Cold environment
            self.genes.cold_resistance += 0.01
            self.genes.heat_resistance -= 0.005
            
        # Humidity adaptations
        if humidity > 0.7:  # Humid environment
            self.genes.humidity_tolerance += 0.01
            self.genes.drought_resistance -= 0.005
        elif humidity < 0.3:  # Dry environment
            self.genes.drought_resistance += 0.01
            self.genes.humidity_tolerance -= 0.005
            
        # UV adaptations
        if uv_level > 0.7:  # High UV
            self.genes.uv_resistance += 0.01
        elif uv_level < 0.3:  # Low UV
            self.genes.uv_resistance -= 0.005
            
        # Elevation adaptations
        if elevation > 2000:  # High altitude
            self.genes.altitude_tolerance += 0.01
            self.genes.oxygen_efficiency += 0.01
        elif elevation < 500:  # Low altitude
            self.genes.altitude_tolerance -= 0.005
            self.genes.oxygen_efficiency -= 0.005
            
        # Terrain-specific adaptations
        if terrain_type:
            if terrain_type == TerrainType.MOUNTAIN:
                self.genes.strength += 0.01
                self.genes.agility += 0.01
            elif terrain_type == TerrainType.WATER:
                self.genes.swimming_ability += 0.01
                self.genes.breath_holding += 0.01
            elif terrain_type == TerrainType.FOREST:
                self.genes.stealth += 0.01
                self.genes.climbing_ability += 0.01
            elif terrain_type == TerrainType.DESERT:
                self.genes.drought_resistance += 0.01
                self.genes.heat_resistance += 0.01
                
        # Weather adaptations
        if weather_type == WeatherType.RAIN:
            self.genes.water_resistance += 0.01
        elif weather_type == WeatherType.SNOW:
            self.genes.cold_resistance += 0.01
        elif weather_type == WeatherType.WINDY:
            self.genes.dust_resistance += 0.01
            
        # Cap all gene values between 0 and 1
        for gene_name in self.genes.__dict__:
            if isinstance(getattr(self.genes, gene_name), float):
                setattr(self.genes, gene_name, max(0.0, min(1.0, getattr(self.genes, gene_name))))

    def get_physical_description(self) -> str:
        """Generate a description of physical appearance based on genes"""
        descriptions = []
        
        # Eye shape
        if self.eye_shape < 0.3:
            descriptions.append("narrow, almond-shaped eyes")
        elif self.eye_shape > 0.7:
            descriptions.append("wide, round eyes")
            
        # Skin tone
        if self.skin_pigment < 0.3:
            descriptions.append("dark skin")
        elif self.skin_pigment > 0.7:
            descriptions.append("light skin")
        else:
            descriptions.append("medium skin tone")
            
        # Nose shape
        if self.nose_shape < 0.3:
            descriptions.append("narrow nose")
        elif self.nose_shape > 0.7:
            descriptions.append("broad nose")
            
        # Body type
        if self.muscle_mass > 0.7:
            descriptions.append("muscular build")
        elif self.muscle_mass < 0.3:
            descriptions.append("lean build")
            
        # Height
        if self.height > 0.7:
            descriptions.append("tall stature")
        elif self.height < 0.3:
            descriptions.append("short stature")
            
        return ", ".join(descriptions)

    def _update_crisis_state(self, world_state: Dict) -> None:
        """Update crisis state based on world conditions"""
        # Check for global crisis indicators
        global_resources = world_state.get("global_resources", {})
        agent_count = len(world_state.get("agents", {}))
        world_size = world_state.get("world_size", 1000)
        
        # Calculate crisis severity based on various factors
        resource_scarcity = 1.0 - (sum(global_resources.values()) / (agent_count * 100))
        population_density = agent_count / world_size
        conflict_level = len(world_state.get("active_conflicts", [])) / agent_count
        
        # Determine crisis type and severity
        self.crisis_state.crisis_severity = max(
            resource_scarcity * 100,
            population_density * 100,
            conflict_level * 100
        )
        
        self.crisis_state.is_crisis = self.crisis_state.crisis_severity > 70
        
        if self.crisis_state.is_crisis:
            if resource_scarcity > 0.8:
                self.crisis_state.crisis_type = "famine"
            elif conflict_level > 0.8:
                self.crisis_state.crisis_type = "war"
            elif population_density > 0.8:
                self.crisis_state.crisis_type = "overpopulation"
            else:
                self.crisis_state.crisis_type = "general_crisis"

    def _handle_crisis_situation(self, current_time: float, world_state: Dict) -> None:
        """Handle behavior during crisis situations"""
        # Increase survival instinct and paranoia
        self.crisis_state.survival_instinct = min(100, self.crisis_state.survival_instinct + 0.1)
        self.crisis_state.paranoia = min(100, self.crisis_state.paranoia + 0.1)
        
        # Check if needs are critical
        if (self.needs.hunger < 20 or self.needs.thirst < 20 or 
            self.needs.health < 20 or self.needs.safety < 20):
            
            # Consider committing crimes if survival is at stake
            if (self.crisis_state.survival_instinct > 70 and 
                current_time - self.crisis_state.last_crime_time > self.crisis_state.crime_cooldown):
                
                self._consider_action(current_time, world_state)
        
        # Update normal needs but with crisis penalties
        self._update_needs(current_time, world_state)
        self._update_emotions(current_time, world_state)
        self._update_relationships(current_time, world_state)
        self._update_health(current_time, world_state)

    def _consider_action(self, current_time: float, world_state: Dict) -> None:
        """Consider and potentially take any action, including violent ones"""
        # Get nearby agents and resources
        nearby_agents = self._get_nearby_agents(world_state)
        nearby_resources = self._get_nearby_resources(world_state)
        
        # Check if we want to establish laws
        if (self.social_state.law_preference > 70 and 
            self.tribe and 
            not self.social_state.has_established_laws):
            self._consider_establishing_laws()
        
        # Consider various actions based on needs and desires
        if self.needs.hunger < 30:
            if nearby_resources:
                self._steal_resources(nearby_resources[0])
            elif nearby_agents:
                self._attack_for_food(nearby_agents[0])
                
        if self.needs.safety < 30:
            if nearby_agents:
                self._attack_for_safety(nearby_agents[0])
                
        if self.social_state.power_seeking > 70:
            if nearby_agents:
                self._attempt_domination(nearby_agents[0])
                
        # Random acts of violence (if inclined)
        if (self.social_state.violence_tolerance > 80 and 
            random.random() < 0.1 and 
            nearby_agents):
            self._commit_random_violence(nearby_agents[0])

    def _get_nearby_resources(self, world_state: Dict, max_distance: float = 50.0) -> List[Dict]:
        """Get all resources within max_distance of this agent's position."""
        nearby_resources = []
        resource_system = world_state.get("resource_system")
        
        if not resource_system:
            return nearby_resources
            
        # Get all resources from the resource system
        resources = resource_system.get_all_resources()
        
        for resource in resources:
            # Calculate distance to resource
            distance = self._calculate_distance(self.position, resource["position"])
            
            if distance <= max_distance:
                nearby_resources.append(resource)
                
        return nearby_resources

    def _steal_resources(self, target_resource: Dict) -> None:
        """Attempt to steal resources from a target."""
        # Calculate success chance based on stealth and strength
        success_chance = (
            self.genes.stealth * 0.4 +
            self.genes.strength * 0.3 +
            random.random() * 0.3  # Random factor
        )
        
        if random.random() < success_chance:
            # Successful theft
            resource_type = target_resource.get("type", "unknown")
            amount = min(target_resource.get("amount", 0), 1.0)  # Steal up to 1.0 units
            
            # Add to inventory
            self.inventory[resource_type] = self.inventory.get(resource_type, 0) + amount
            
            # Record crime
            self.social_state.crimes_committed.append({
                "type": "theft",
                "resource_type": resource_type,
                "amount": amount,
                "timestamp": time.time()
            })
            
            # Add memory
            self.add_memory(
                f"Stole {amount} {resource_type}",
                0.6,
                {
                    "resource_type": resource_type,
                    "amount": amount,
                    "success": True
                },
                emotional_impact=0.4
            )
            
            # Update moral state
            self.crisis_state.moral_compromise = min(100, self.crisis_state.moral_compromise + 5)
            
    def _attack_for_food(self, target: Dict) -> None:
        """Attack another agent for food or meat."""
        success_chance = (
            self.genes.strength * 0.4 +
            self.genes.hunting_skill * 0.3 +
            random.random() * 0.3
        )
        if random.random() < success_chance:
            self.social_state.crimes_committed.append({
                "type": "attack_for_food",
                "target": target["id"],
                "success": True,
                "timestamp": time.time()
            })
            # Take food or meat resources
            if "meat" in target.get("inventory", {}):
                meat_amount = min(target["inventory"]["meat"], 1.0)
                self.inventory[FoodType.RAW_MEAT.value] = self.inventory.get(FoodType.RAW_MEAT.value, 0) + meat_amount
            elif "food" in target.get("inventory", {}):
                food_amount = min(target["inventory"]["food"], 1.0)
                self.inventory[FoodType.RAW_VEGETABLES.value] = self.inventory.get(FoodType.RAW_VEGETABLES.value, 0) + food_amount
            self.add_memory(
                f"Attacked {target['name']} for food",
                0.7,
                {
                    "target_id": target["id"],
                    "target_name": target["name"],
                    "success": True
                },
                emotional_impact=0.6
            )
            self.crisis_state.moral_compromise = min(100, self.crisis_state.moral_compromise + 10)
            
    def _attack_for_safety(self, target: Dict) -> None:
        """Attack another agent for safety."""
        # Calculate attack success chance
        success_chance = (
            self.genes.strength * 0.4 +
            self.genes.stealth * 0.3 +
            random.random() * 0.3  # Random factor
        )
        
        if random.random() < success_chance:
            # Successful attack
            self.social_state.crimes_committed.append({
                "type": "attack_for_safety",
                "target": target["id"],
                "success": True,
                "timestamp": time.time()
            })
            
            # Add memory
            self.add_memory(
                f"Attacked {target['name']} for safety",
                0.7,
                {
                    "target_id": target["id"],
                    "target_name": target["name"],
                    "success": True
                },
                emotional_impact=0.6
            )
            
            # Update moral state
            self.crisis_state.moral_compromise = min(100, self.crisis_state.moral_compromise + 5)
            
    def _attempt_domination(self, target: Dict) -> None:
        """Attempt to dominate another agent."""
        # Calculate domination success chance
        success_chance = (
            self.genes.strength * 0.3 +
            self.genes.social_drive * 0.3 +
            self.social_state.power_seeking * 0.2 +
            random.random() * 0.2  # Random factor
        )
        
        if random.random() < success_chance:
            # Successful domination
            self.social_state.crimes_committed.append({
                "type": "domination",
                "target": target["id"],
                "success": True,
                "timestamp": time.time()
            })
            
            # Add memory
            self.add_memory(
                f"Successfully dominated {target['name']}",
                0.8,
                {
                    "target_id": target["id"],
                    "target_name": target["name"],
                    "success": True
                },
                emotional_impact=0.7
            )
            
            # Update moral state
            self.crisis_state.moral_compromise = min(100, self.crisis_state.moral_compromise + 15)
            
    def _commit_random_violence(self, target: Dict) -> None:
        """Commit random act of violence."""
        # Calculate violence success chance
        success_chance = (
            self.genes.strength * 0.4 +
            self.genes.stealth * 0.3 +
            random.random() * 0.3  # Random factor
        )
        
        if random.random() < success_chance:
            # Successful violence
            violence_type = random.choice(["attack", "murder", "kidnapping", "torture"])
            self.social_state.crimes_committed.append({
                "type": violence_type,
                "target": target["id"],
                "success": True,
                "timestamp": time.time()
            })
            
            # Add memory
            self.add_memory(
                f"Committed {violence_type} against {target['name']}",
                0.9,
                {
                    "target_id": target["id"],
                    "target_name": target["name"],
                    "violence_type": violence_type,
                    "success": True
                },
                emotional_impact=0.8
            )
            
            # Update moral state
            self.crisis_state.moral_compromise = min(100, self.crisis_state.moral_compromise + 20)
            
    def _consider_establishing_laws(self) -> None:
        """Consider establishing laws in their tribe."""
        if random.random() < self.social_state.law_preference / 100:
            # Create basic laws
            self.social_state.laws = {
                "murder": {
                    "punishment": "death",
                    "severity": 100,
                    "established_by": self.id
                },
                "theft": {
                    "punishment": "exile",
                    "severity": 70,
                    "established_by": self.id
                },
                "assault": {
                    "punishment": "imprisonment",
                    "severity": 50,
                    "established_by": self.id
                }
            }
            self.social_state.has_established_laws = True
            self.social_state.is_lawful = True
            
            # Add memory
            self.add_memory(
                "Established laws in tribe",
                0.9,
                {
                    "laws": self.social_state.laws,
                    "tribe": self.tribe
                },
                emotional_impact=0.7,
                philosophical_impact=0.6
            )

    def _update_needs(self, current_time: float, world_state: Dict):
        """Update agent's needs over time."""
        # Decrease needs based on time and metabolism
        metabolism_factor = self.genes.metabolism
        
        # Basic needs
        self.needs.hunger = max(0.0, self.needs.hunger - 0.1 * current_time * metabolism_factor)
        self.needs.thirst = max(0.0, self.needs.thirst - 0.2 * current_time * metabolism_factor)
        self.needs.rest = max(0.0, self.needs.rest - 0.05 * current_time)
        
        # Social needs
        if not self.tribe and not self.mate:
            self.needs.social = max(0.0, self.needs.social - 0.1 * current_time)
            
        # Creative needs
        if self.genes.creativity > 0.7:
            self.needs.creative_expression = max(0.0, self.needs.creative_expression - 0.05 * current_time)
            
        # Philosophical needs
        if self.genes.philosophical_tendency > 0.7:
            self.needs.philosophical_expression = max(0.0, self.needs.philosophical_expression - 0.05 * current_time)
            
        # Reproduction needs
        if self.life_stage == LifeStage.ADULT and not self.mate:
            self.needs.reproduction = max(0.0, self.needs.reproduction - 0.05 * current_time)
            
        # Increase bathroom needs
        self.needs.bladder = min(1.0, self.needs.bladder + 0.02)
        self.needs.bowel = min(1.0, self.needs.bowel + 0.01)
        
        # Decrease hygiene over time
        self.needs.hygiene = max(0.0, self.needs.hygiene - 0.005)
        
        # Increase reproduction urge over time
        self.needs.reproduction_urge = min(1.0, self.needs.reproduction_urge + 0.001)
        
        # Log urgent needs
        if self.needs.bladder > 0.8:
            logger.info(f"Agent {self.id} ({self.name}) needs to urinate")
        if self.needs.bowel > 0.8:
            logger.info(f"Agent {self.id} ({self.name}) needs to defecate")
        if self.needs.hygiene < 0.3:
            logger.info(f"Agent {self.id} ({self.name}) needs to clean themselves")

    def _update_emotions(self, current_time: float, world_state: Dict):
        """Process and update emotions based on current state."""
        # Update existing emotions
        self.emotions.update_emotions(1.0)  # 1 hour time delta
        
        # Get current emotional state
        emotional_state = self.emotions.get_current_emotional_state()
        
        # Check for existential triggers
        if self.genes.existential_awareness > 0.7:
            if self.age > 20 and random.random() < 0.1:  # More likely to question existence as they age
                self._trigger_existential_thought()
                
        # Check for suicidal thoughts
        if (emotional_state.get("suicidal_tendency", 0.0) > 0.7 and 
            self.philosophy.suicidal_thoughts > 0.7 and 
            random.random() < 0.1):
            self._consider_suicide(world_state)
                
        # Check for emotional expression needs
        if self.needs.emotional_expression < 0.3:
            self._express_emotions()
            
    def _trigger_existential_thought(self):
        """Trigger existential questioning based on current state."""
        # Get current emotional state
        emotional_state = self.emotions.get_current_emotional_state()
        
        # Form existential questions based on emotions
        questions = []
        
        if EmotionType.EXISTENTIAL_DREAD in emotional_state["emotions"]:
            questions.append("Why do we exist?")
            questions.append("What happens after death?")
            
        if EmotionType.MEANING in emotional_state["emotions"]:
            questions.append("What is the meaning of life?")
            questions.append("Do we have a purpose?")
            
        if EmotionType.CONNECTION in emotional_state["emotions"]:
            questions.append("Are we alone in the universe?")
            questions.append("Do others experience the same emotions?")
            
        # Try to develop philosophical concepts from these questions
        for question in questions:
            concept = self.philosophy.ponder_existence({
                "memories": self.memories,
                "discovered_concepts": self.discovered_concepts,
                "understanding_levels": self.understanding_levels,
                "current_question": question
            })
            
            if concept:
                # Add to discovered concepts
                self.discovered_concepts.add(concept.name)
                self.understanding_levels[concept.name] = concept.confidence
                
                # Add to memory with high philosophical impact
                self.add_memory(
                    f"Developed philosophical concept: {concept.name}",
                    0.9,  # Very high importance
                    {
                        "concept": concept.name,
                        "description": concept.description,
                        "confidence": concept.confidence,
                        "implications": concept.implications,
                        "question": question
                    },
                    philosophical_impact=0.8
                )
                
                # Update needs
                self.needs.purpose = min(1.0, self.needs.purpose + 0.2)
                self.needs.understanding = min(1.0, self.needs.understanding + 0.2)
                self.needs.philosophical_expression = min(1.0, self.needs.philosophical_expression + 0.3)
                
    def _express_emotions(self):
        """Express emotions through various means."""
        emotional_state = self.emotions.get_current_emotional_state()
        
        # Find dominant emotions
        dominant_emotions = [
            (emotion_type, data)
            for emotion_type, data in emotional_state["emotions"].items()
            if data["intensity"] > 0.7
        ]
        
        if not dominant_emotions:
            return
            
        # Choose expression method based on emotions
        for emotion_type, data in dominant_emotions:
            if emotion_type in [EmotionType.JOY, EmotionType.LOVE]:
                # Express through art or music
                self._create_artistic_expression(emotion_type, data)
            elif emotion_type in [EmotionType.SADNESS, EmotionType.LONELINESS]:
                # Express through writing or poetry
                self._create_written_expression(emotion_type, data)
            elif emotion_type in [EmotionType.WONDER, EmotionType.AWE]:
                # Express through philosophical writing
                self._create_philosophical_expression(emotion_type, data)
                
        # Update emotional expression need
        self.needs.emotional_expression = min(1.0, self.needs.emotional_expression + 0.3)
        
    def _create_artistic_expression(self, emotion_type: str, emotion_data: Dict):
        """Create artistic expression of emotions."""
        # Add to discovered concepts
        self.discovered_concepts.add("artistic_expression")
        self.understanding_levels["artistic_expression"] = 0.5
        
        # Add to memory
        self.add_memory(
            f"Created artistic expression of {emotion_type}",
            0.7,
            {
                "emotion": emotion_type,
                "intensity": emotion_data["intensity"],
                "expression_type": "art",
                "associated_memories": emotion_data["associated_memories"]
            },
            emotional_impact=0.8
        )
        
    def _create_written_expression(self, emotion_type: str, emotion_data: Dict):
        """Create written expression of emotions."""
        # Add to discovered concepts
        self.discovered_concepts.add("written_expression")
        self.understanding_levels["written_expression"] = 0.5
        
        # Add to memory
        self.add_memory(
            f"Created written expression of {emotion_type}",
            0.7,
            {
                "emotion": emotion_type,
                "intensity": emotion_data["intensity"],
                "expression_type": "writing",
                "associated_memories": emotion_data["associated_memories"]
            },
            emotional_impact=0.8
        )
        
    def _create_philosophical_expression(self, emotion_type: str, emotion_data: Dict):
        """Create philosophical expression of emotions."""
        # Add to discovered concepts
        self.discovered_concepts.add("philosophical_expression")
        self.understanding_levels["philosophical_expression"] = 0.5
        
        # Add to memory
        self.add_memory(
            f"Created philosophical expression of {emotion_type}",
            0.8,
            {
                "emotion": emotion_type,
                "intensity": emotion_data["intensity"],
                "expression_type": "philosophy",
                "associated_memories": emotion_data["associated_memories"],
                "associated_concepts": list(emotion_data["associated_concepts"])
            },
            emotional_impact=0.8,
            philosophical_impact=0.7
        )
        
    def add_memory(self, event: str, importance: float, context: Optional[Dict] = None,
                  emotional_impact: float = 0.0, philosophical_impact: float = 0.0,
                  cognitive_impact: float = 0.0) -> None:
        """Add a new memory with emotional, philosophical, and cognitive impact."""
        memory = Memory(
            event=event,
            importance=importance,
            timestamp=datetime.now(),
            context=context or {},
            concepts=set(),
            animal_interactions=self.animal_interactions,
            domesticated_animals=self.domesticated_animals,
            emotional_impact=emotional_impact,
            philosophical_impact=philosophical_impact,
            cognitive_impact=cognitive_impact
        )
        
        # Extract concepts from event
        for concept in self.discovered_concepts:
            if concept.lower() in event.lower():
                memory.concepts.add(concept)
                
        self.memories.append(memory)
        
        # Keep important memories separate
        if importance > 0.7:
            self.important_memories.append(memory)
            
        # Process emotions from this memory
        self.emotions.process_experience(event, context or {}, self.to_dict())
        
        # Process thoughts from this memory
        self.cognition.process_experience(event, context or {}, self.to_dict())
        
        # Update cognition state
        self.cognition_state = {
            "memories": self.memories,
            "important_memories": self.important_memories,
            "current_thoughts": self.cognition.current_thoughts if hasattr(self.cognition, 'current_thoughts') else "",
            "last_action": self.cognition.last_action if hasattr(self.cognition, 'last_action') else None
        }

    def _update_animal_interactions(self, current_time: float, world_state: Dict) -> None:
        """Update interactions with animals in the environment."""
        # Get animal system from world state
        animal_system = world_state.get("animal_system")
        if not animal_system:
            return
            
        # Get nearby animals
        nearby_animals = animal_system.get_nearby_animals(self.position, max_distance=50.0)
        
        for animal in nearby_animals:
            # Skip if already owned
            if animal.owner_id == self.id:
                continue
                
            # Check if we should try to tame
            if (self.needs.animal_companionship > 0.7 and 
                not animal.domesticated and 
                animal.temperament != AnimalTemperament.WILD):
                
                # Calculate taming success chance
                success_chance = (
                    self.genes.animal_affinity * 0.4 +
                    self.genes.taming_skill * 0.4 +
                    random.random() * 0.2  # Random factor
                )
                
                if random.random() < success_chance:
                    # Attempt to tame
                    if animal_system.attempt_taming(animal, self.to_dict()):
                        self.domesticated_animals.append(animal.id)
                        self.add_memory(
                            f"Successfully tamed a {animal.name}",
                            0.8,  # High importance
                            {
                                "animal_id": animal.id,
                                "animal_type": animal.type.value,
                                "temperament": animal.temperament.value
                            },
                            emotional_impact=0.8,
                            philosophical_impact=0.3
                        )
                        
            # Check if we should try to hunt
            elif (self.needs.hunting_urge > 0.8 and 
                  animal.type in [AnimalType.CARNIVORE, AnimalType.OMNIVORE]):
                
                # Calculate hunting success chance
                success_chance = (
                    self.genes.hunting_skill * 0.4 +
                    self.genes.strength * 0.3 +
                    self.genes.stealth * 0.3
                )
                
                if random.random() < success_chance:
                    # Successful hunt
                    self.add_memory(
                        f"Successfully hunted a {animal.name}",
                        0.7,  # High importance
                        {
                            "animal_id": animal.id,
                            "animal_type": animal.type.value,
                            "hunting_method": "direct_hunt"
                        },
                        emotional_impact=0.6,
                        philosophical_impact=0.2
                    )
                    # Add meat to inventory
                    meat_amount = random.uniform(5.0, 15.0)
                    self.inventory[FoodType.RAW_MEAT.value] = self.inventory.get(FoodType.RAW_MEAT.value, 0) + meat_amount
                    
            # Check if we should try to train (for owned animals)
            elif animal.owner_id == self.id:
                # Calculate training success chance
                success_chance = (
                    self.genes.animal_affinity * 0.4 +
                    self.genes.taming_skill * 0.4 +
                    random.random() * 0.2  # Random factor
                )
                
                if random.random() < success_chance:
                    # Attempt to train
                    training_progress = animal_system.train_animal(animal, self.to_dict())
                    if training_progress > 0:
                        self.add_memory(
                            f"Successfully trained {animal.name}",
                            0.6,  # Medium importance
                            {
                                "animal_id": animal.id,
                                "animal_type": animal.type.value,
                                "training_progress": training_progress
                            },
                            emotional_impact=0.4,
                            philosophical_impact=0.2
                        )
                        
        # Update animal-related needs
        if self.domesticated_animals:
            self.needs.animal_companionship = min(1.0, self.needs.animal_companionship + 0.1)
        else:
            self.needs.animal_companionship = max(0.0, self.needs.animal_companionship - 0.05)
            
        # Update hunting urge based on meat in inventory
        if self.inventory.get(FoodType.RAW_MEAT.value, 0) > 10.0:
            self.needs.hunting_urge = max(0.0, self.needs.hunting_urge - 0.1)
        else:
            self.needs.hunting_urge = min(1.0, self.needs.hunting_urge + 0.05)

    def train_animal(self, animal_id: str, world_state: Dict) -> float:
        """Train a domesticated animal. Returns training progress made."""
        if animal_id not in self.memory.domesticated_animals:
            return 0.0
            
        animal = world_state["animal_system"].animals.get(animal_id)
        if not animal or animal.owner_id != self.id:
            return 0.0
            
        progress = world_state["animal_system"].train_animal(animal, self.to_dict())
        
        if progress > 0:
            self.add_memory(
                f"Trained {animal.name}",
                "animal_training",
                emotional_impact=0.4,
                philosophical_impact=0.2
            )
            
        return progress
        
    def _handle_bathroom_needs(self, world_state: Dict) -> None:
        """Handle bathroom needs"""
        # Find nearest bathroom facility
        bathroom_facilities = world_state.get("bathroom_facilities", [])
        if bathroom_facilities:
            nearest = min(bathroom_facilities, key=lambda f: self._calculate_distance(self.position, f["position"]))
            distance = self._calculate_distance(self.position, nearest["position"])
            
            if distance < 5:  # Within bathroom range
                # Use bathroom
                if self.needs.bladder > 0.5:
                    self.needs.bladder = 0.0
                    logger.info(f"Agent {self.id} ({self.name}) used bathroom for urination")
                if self.needs.bowel > 0.5:
                    self.needs.bowel = 0.0
                    logger.info(f"Agent {self.id} ({self.name}) used bathroom for defecation")
                # Clean up
                self.needs.hygiene = min(1.0, self.needs.hygiene + 0.2)
            else:
                # Move towards bathroom
                self._move_towards(nearest["position"])
        else:
            # If no bathroom facilities, find a secluded spot
            if self.needs.bladder > 0.9 or self.needs.bowel > 0.9:
                # Find secluded spot (away from other agents)
                secluded_spot = self._find_secluded_spot(world_state)
                if secluded_spot:
                    self._move_towards(secluded_spot)
                    if self._calculate_distance(self.position, secluded_spot) < 5:
                        # Use secluded spot
                        if self.needs.bladder > 0.5:
                            self.needs.bladder = 0.0
                            logger.info(f"Agent {self.id} ({self.name}) relieved themselves in secluded spot")
                        if self.needs.bowel > 0.5:
                            self.needs.bowel = 0.0
                            logger.info(f"Agent {self.id} ({self.name}) relieved themselves in secluded spot")
                        # Hygiene penalty for using secluded spot
                        self.needs.hygiene = max(0.0, self.needs.hygiene - 0.1)

    def _find_secluded_spot(self, world_state: Dict) -> Optional[Tuple[float, float]]:
        """Find a secluded spot away from other agents"""
        agents = world_state.get("agents", {})
        if not agents:
            return None
        
        # Try random positions until finding a secluded one
        for _ in range(10):
            x = random.uniform(0, self.world_size)
            y = random.uniform(0, self.world_size)
            position = (x, y)
            
            # Check if position is secluded (no agents within 20 units)
            is_secluded = True
            for agent in agents.values():
                if self._calculate_distance(position, agent["position"]) < 20:
                    is_secluded = False
                    break
                
            if is_secluded:
                return position
            
        return None

    def _update_behavior(self, current_time: float, world_state: Dict) -> None:
        """Update agent behavior based on current state and needs."""
        # Handle bathroom needs first if urgent
        if self.needs.bladder > 0.8 or self.needs.bowel > 0.8:
            self._handle_bathroom_needs(world_state)
            return
            
        # Handle other needs
        if self.needs.hunger < 0.3:
            self._seek_food(world_state)
        elif self.needs.thirst < 0.3:
            self._seek_water(world_state)
        elif self.needs.energy < 0.3:
            self._rest()
        elif self.needs.hygiene < 0.3:
            self._clean_self(world_state)
        elif self.needs.social < 0.3:
            self._seek_social_interaction(world_state)
        elif self.needs.creative_expression < 0.3:
            self._express_creativity()
        elif self.needs.philosophical_expression < 0.3:
            self._express_philosophy()
        else:
            self._consider_action(current_time, world_state)

    def _clean_self(self, world_state: Dict) -> None:
        """Clean self if water is available"""
        water_sources = world_state.get("water_sources", [])
        if water_sources:
            nearest = min(water_sources, key=lambda w: self._calculate_distance(self.position, w["position"]))
            distance = self._calculate_distance(self.position, nearest["position"])
            
            if distance < 5:  # Within water range
                self.needs.hygiene = min(1.0, self.needs.hygiene + 0.2)
                logger.info(f"Agent {self.id} ({self.name}) cleaned themselves")
            else:
                self._move_towards(nearest["position"])

    def _consider_suicide(self, world_state: Dict):
        """Consider and potentially attempt suicide."""
        # Check if there are reasons to live
        reasons_to_live = []
        
        # Check for family
        if self.mate or self.children:
            reasons_to_live.append("family")
            
        # Check for tribe
        if self.tribe:
            reasons_to_live.append("tribe")
            
        # Check for recent positive experiences
        recent_memories = [m for m in self.memories[-10:] if m.importance > 0.7]
        if recent_memories:
            reasons_to_live.append("recent_positive_experiences")
            
        # If no strong reasons to live and high suicidal tendency
        if (not reasons_to_live and 
            self.emotions.emotional_state.get("suicidal_tendency", 0.0) > 0.8 and 
            self.philosophy.suicidal_thoughts > 0.8):
            
            # Attempt suicide
            self._attempt_suicide(world_state)
        else:
            # Add memory of considering suicide
            self.add_memory(
                "Considered ending own life",
                0.9,
                {
                    "reasons_to_live": reasons_to_live,
                    "emotional_state": self.emotions.get_current_emotional_state(),
                    "philosophical_state": self.philosophy.to_dict()
                },
                emotional_impact=0.9,
                philosophical_impact=0.8
            )
            
    def _attempt_suicide(self, world_state: Dict):
        """Attempt to end own life."""
        # Add memory of suicide attempt
        self.add_memory(
            "Attempted to end own life",
            1.0,
            {
                "emotional_state": self.emotions.get_current_emotional_state(),
                "philosophical_state": self.philosophy.to_dict(),
                "final_thoughts": self._generate_final_thoughts()
            },
            emotional_impact=1.0,
            philosophical_impact=1.0
        )
        
        # Log the event
        logger.info(f"Agent {self.id} ({self.name}) has ended their life")
        
        # Mark agent as dead
        self.health = 0.0
        
    def _generate_final_thoughts(self) -> str:
        """Generate final thoughts before death."""
        thoughts = [
            "The pain is finally over",
            "I hope they understand",
            "Maybe in another life",
            "I'm sorry",
            "I just couldn't go on",
            "The world is better without me",
            "I'm finally free",
            "No more suffering",
            "I hope they find peace",
            "Goodbye"
        ]
        return random.choice(thoughts)

    def _update_relationships(self, current_time: float, world_state: Dict) -> None:
        """Update relationships with other agents"""
        # Get nearby agents
        nearby_agents = self._get_nearby_agents(world_state)
        
        for other_agent in nearby_agents:
            if other_agent["id"] == self.id:  # Access id from dictionary
                continue
                
            # Calculate relationship factors
            compatibility = self._calculate_compatibility(other_agent)
            attractiveness = self._calculate_attraction(other_agent)
            shared_interests = self._calculate_shared_interests(other_agent)
            
            # Update relationship
            if other_agent["id"] not in self.relationships:  # Access id from dictionary
                self.relationships[other_agent["id"]] = {
                    "compatibility": compatibility,
                    "attraction": attractiveness,
                    "shared_interests": shared_interests,
                    "trust": 0.5,
                    "affection": 0.5,
                    "last_interaction": current_time
                }
            else:
                rel = self.relationships[other_agent["id"]]
                rel["compatibility"] = (rel["compatibility"] + compatibility) / 2
                rel["attraction"] = (rel["attraction"] + attractiveness) / 2
                rel["shared_interests"] = (rel["shared_interests"] + shared_interests) / 2
                
            # Check for potential romantic interest
            if (self.life_stage == LifeStage.ADULT and 
                not self.mate and 
                not other_agent.get("mate") and  # Access mate from dictionary
                self.relationships[other_agent["id"]]["attraction"] > 0.7 and
                self.relationships[other_agent["id"]]["compatibility"] > 0.6):
                
                self._consider_romantic_interest(other_agent)
                
    def _calculate_attraction(self, other_agent: Dict) -> float:
        """Calculate attraction to another agent based on physical and personality traits"""
        # Use default cultural preferences
        cultural_preferences = {
            "facial_symmetry": 0.8,
            "body_proportion": 0.7,
            "skin_quality": 0.6,
            "hair_quality": 0.5,
            "height": 0.4,
            "muscle_tone": 0.3,
            "voice_quality": 0.4,
            "eye_color": 0.3,
            "hair_color": 0.3
        }
        
        # Calculate physical attraction using dictionary access
        physical_traits = {
            trait: other_agent["genes"].get(trait, 0.5)
            for trait in cultural_preferences.keys()
        }
        
        # Calculate weighted average of physical traits
        total_weight = sum(cultural_preferences.values())
        physical_attraction = sum(
            physical_traits[trait] * weight 
            for trait, weight in cultural_preferences.items()
        ) / total_weight
        
        # Calculate personality attraction
        personality_attraction = (
            other_agent["genes"].get("intelligence", 0.5) * 0.3 +
            other_agent["genes"].get("social_drive", 0.5) * 0.2 +
            other_agent["genes"].get("emotional_depth", 0.5) * 0.2 +
            other_agent["genes"].get("creativity", 0.5) * 0.15 +
            other_agent["genes"].get("philosophical_tendency", 0.5) * 0.15
        )
        
        # Combine physical and personality attraction
        total_attraction = (physical_attraction * 0.6 + personality_attraction * 0.4)
        
        # Modify based on personal preferences if they exist
        if hasattr(self, 'preferences') and hasattr(self.preferences, 'preferred_traits'):
            for trait, weight in self.preferences.preferred_traits.items():
                if trait in other_agent["genes"]:
                    total_attraction *= (1 + (other_agent["genes"][trait] * weight))
                        
        return min(1.0, total_attraction)
        
    def _consider_romantic_interest(self, other_agent: Dict) -> None:
        """Consider pursuing a romantic relationship with another agent"""
        # Check if both agents are interested
        if (self.relationships[other_agent["id"]]["attraction"] > 0.7 and
            other_agent.get("relationships", {}).get(self.id, {}).get("attraction", 0) > 0.7):
            
            # Calculate relationship potential
            potential = (
                self.relationships[other_agent["id"]]["compatibility"] * 0.4 +
                self.relationships[other_agent["id"]]["attraction"] * 0.4 +
                self.relationships[other_agent["id"]]["shared_interests"] * 0.2
            )
            
            if potential > 0.7:  # High potential for relationship
                # Propose relationship
                if random.random() < 0.3:  # 30% chance to propose
                    self._propose_relationship(other_agent)
                    
    def _propose_relationship(self, other_agent: Dict) -> None:
        """Propose a romantic relationship to another agent"""
        # Check if other agent accepts
        acceptance_chance = (
            other_agent.get("relationships", {}).get(self.id, {}).get("attraction", 0) * 0.6 +
            other_agent.get("relationships", {}).get(self.id, {}).get("compatibility", 0) * 0.4
        )
        
        if random.random() < acceptance_chance:
            # Form relationship
            self.mate = other_agent["id"]
            # Note: We can't directly modify other_agent's mate since it's a dictionary
            # This will need to be handled by the world update system
            
            # Update relationship status
            self.relationships[other_agent["id"]]["status"] = "romantic"
            
            # Log relationship formation
            logger.info(f"Agents {self.id} and {other_agent['id']} entered a romantic relationship")
            
            # Process emotional impact
            self.emotions.process_experience(
                "Formed romantic relationship",
                {"partner": other_agent["id"]},
                self.to_dict()
            )

    def get_recent_memories(self, count: int = 5) -> List[Memory]:
        """Get the most recent memories, ordered by timestamp."""
        # Sort memories by timestamp in descending order and return the most recent ones
        sorted_memories = sorted(self.memories, key=lambda m: m.timestamp, reverse=True)
        return sorted_memories[:count]

    def update_needs(self, time_delta: float) -> None:
        """Update agent's needs based on time passed."""
        # Update basic needs
        self.needs.hunger = max(0.0, self.needs.hunger - 0.1 * time_delta)
        self.needs.thirst = max(0.0, self.needs.thirst - 0.2 * time_delta)
        self.needs.rest = max(0.0, self.needs.rest - 0.05 * time_delta)
        
        # Update social needs if no tribe or mate
        if not self.tribe and not self.mate:
            self.needs.social = max(0.0, self.needs.social - 0.1 * time_delta)
            
        # Update creative needs if agent is creative
        if self.genes.creativity > 0.7:
            self.needs.creative_expression = max(0.0, self.needs.creative_expression - 0.05 * time_delta)
            
        # Update philosophical needs if agent is philosophical
        if self.genes.philosophical_tendency > 0.7:
            self.needs.philosophical_expression = max(0.0, self.needs.philosophical_expression - 0.05 * time_delta)
            
        # Update reproduction needs if adult and no mate
        if self.life_stage == LifeStage.ADULT and not self.mate:
            self.needs.reproduction = max(0.0, self.needs.reproduction - 0.05 * time_delta)
            
        # Update bathroom needs
        self.needs.bladder = min(1.0, self.needs.bladder + 0.02 * time_delta)
        self.needs.bowel = min(1.0, self.needs.bowel + 0.01 * time_delta)
        
        # Update hygiene
        self.needs.hygiene = max(0.0, self.needs.hygiene - 0.005 * time_delta)
        
        # Update reproduction urge
        self.needs.reproduction_urge = min(1.0, self.needs.reproduction_urge + 0.001 * time_delta)
        
        # Log urgent needs
        if self.needs.bladder > 0.8:
            logger.info(f"Agent {self.id} ({self.name}) needs to urinate")
        if self.needs.bowel > 0.8:
            logger.info(f"Agent {self.id} ({self.name}) needs to defecate")
        if self.needs.hygiene < 0.3:
            logger.info(f"Agent {self.id} ({self.name}) needs to clean themselves")

    def _get_nearby_agents(self, world_state: Dict, max_distance: float = 50.0) -> List[Dict]:
        """Get all agents within max_distance of this agent's position."""
        nearby_agents = []
        
        for agent_id, agent in world_state.get("agents", {}).items():
            if agent_id != self.id:  # Don't include self
                distance = self._calculate_distance(agent["longitude"], agent["latitude"])
                if distance <= max_distance:
                    nearby_agents.append(agent)
                    
        return nearby_agents
        
    def _calculate_distance(self, other_longitude: float, other_latitude: float) -> float:
        """Calculate distance between two points using the Haversine formula."""
        from math import radians, sin, cos, sqrt, atan2
        
        # Convert to radians
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other_latitude), radians(other_longitude)
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = 6371 * c  # Earth's radius in km
        
        return distance

    def _move_towards(self, target_longitude: float, target_latitude: float) -> None:
        """Move towards a target position using longitude and latitude."""
        # Calculate direction vector
        dlon = target_longitude - self.longitude
        dlat = target_latitude - self.latitude
        
        # Normalize direction
        distance = self._calculate_distance(target_longitude, target_latitude)
        if distance > 0:
            dlon /= distance
            dlat /= distance
            
            # Move (0.01 degrees per step, approximately 1.1 km)
            self.longitude += dlon * 0.01
            self.latitude += dlat * 0.01

    def _get_nearby_resources(self, world_state: Dict, max_distance: float = 50.0) -> List[Dict]:
        """Get all resources within max_distance of this agent's position."""
        nearby_resources = []
        resource_system = world_state.get("resource_system")
        
        if not resource_system:
            return nearby_resources
            
        # Get all resources from the resource system
        resources = resource_system.get_all_resources()
        
        for resource in resources:
            # Calculate distance to resource
            distance = self._calculate_distance(resource["longitude"], resource["latitude"])
            
            if distance <= max_distance:
                nearby_resources.append(resource)
                
        return nearby_resources

    def has_discovered(self, tech_name: str) -> bool:
        """Check if agent has discovered a technology or skill."""
        # This should check the agent's known discoveries or the world's discovery/technology system
        if hasattr(self, 'known_discoveries') and tech_name in self.known_discoveries:
            return True
        if hasattr(self.world, 'discovery') and hasattr(self.world.discovery, 'discovered'):
            return tech_name in self.world.discovery.discovered
        if hasattr(self.world, 'technology') and hasattr(self.world.technology, 'discovered_techs'):
            return tech_name in self.world.technology.discovered_techs
            return False
            
    def fish(self, longitude: float, latitude: float, method: str = "net") -> dict:
        """Attempt to fish at a location, only if agent has discovered fishing."""
        # Only allow fishing if agent has discovered fishing
        if not self.has_discovered("fishing"):
            if hasattr(self, 'logger'):
                self.logger.info(f"Agent {getattr(self, 'id', '?')} tried to fish but hasn't discovered fishing.")
            return {}
        if not self._can_fish(longitude, latitude):
            return {}
        # Use MarineSystem for fish yield
        marine = getattr(self.world, 'marine', None)
        if not marine:
            return {}
        # Get fish yield from marine system
        time_delta = 1.0  # One hour of fishing
        fish_yield = marine.get_fishing_yield(longitude, latitude, time_delta) if hasattr(marine, 'get_fishing_yield') else {}
        if not fish_yield:
            return {}
        # Add fish to inventory
        fish_amount = fish_yield.get('fish', 0)
        if fish_amount > 0:
            self.inventory[FoodType.RAW_FISH.value] = self.inventory.get(FoodType.RAW_FISH.value, 0) + fish_amount
        # Record fishing activity
        self.fishing_history.append({
            "time": self.world.get_current_game_time(),
            "longitude": longitude,
            "latitude": latitude,
            "method": method,
            "success": bool(fish_amount),
            "yield": fish_yield
        })
        return fish_yield

    def has_discovered(self, tech_name: str) -> bool:
        """Check if agent has discovered a technology or skill."""
            "success": bool(yield_dict),
            "yield": yield_dict
        })
        
        return yield_dict

    def _can_fish(self, longitude: float, latitude: float) -> bool:
        """Check if agent can fish at a location."""
        # Check if position is in ocean
        if not self.world.terrain._is_ocean(longitude, latitude):
            return False
            
        # Check if agent has required tools
        if not self._has_fishing_tools():
            return False
            
        # Check if agent is close enough to water
        distance = self._calculate_distance(longitude, latitude)
        if distance > 0.1:  # Must be within 0.1 degrees
            return False
            
        return True
        
    def _has_fishing_tools(self) -> bool:
        """Check if agent has fishing tools."""
        return any(tool["type"] in ["net", "rod", "spear"] for tool in self.fishing_tools.values())
        
    def _get_method_efficiency(self, method: str) -> float:
        """Get efficiency of fishing method based on skill and tools."""
        base_efficiency = {
            "net": 0.6,
            "rod": 0.4,
            "spear": 0.3,
            "trap": 0.5
        }.get(method, 0.2)
        
        # Modify by skill
        efficiency = base_efficiency * (0.5 + self.fishing_skill)
        
        # Modify by tools
        tool_bonus = 0.0
        for tool in self.fishing_tools.values():
            if tool["type"] == method:
                tool_bonus += 0.2
                
        return min(1.0, efficiency + tool_bonus)
        
    def _update_skills(self, current_time: float, world_state: Dict) -> None:
        """Update and improve agent's skills based on activities and experience."""
        # Get current activities and environment
        environment = world_state.get("environment", {})
        terrain = environment.get_terrain_at(self.position[0], self.position[1])
        weather = environment.get_weather_at(self.position[0], self.position[1])
        
        # Update physical skills based on terrain and activities
        if terrain and terrain.type == TerrainType.MOUNTAIN:
            self.genes.strength += 0.001
            self.genes.climbing_ability += 0.001
        elif terrain and terrain.type == TerrainType.WATER:
            self.genes.swimming_ability += 0.001
            self.genes.breath_holding += 0.001
        elif terrain and terrain.type == TerrainType.FOREST:
            self.genes.stealth += 0.001
            self.genes.hunting_skill += 0.001
            
        # Update survival skills based on weather
        if weather and weather["type"] == WeatherType.RAIN:
            self.genes.water_resistance += 0.001
        elif weather and weather["type"] == WeatherType.SNOW:
            self.genes.cold_resistance += 0.001
        elif weather and weather["type"] == WeatherType.WINDY:
            self.genes.dust_resistance += 0.001
            
        # Update social and cognitive skills based on interactions
        if self.needs.social < 0.5:  # If social need is high
            self.genes.social_drive += 0.001
            self.genes.emotional_depth += 0.001
            
        # Update creative and philosophical skills
        if self.needs.creative_expression < 0.5:
            self.genes.creativity += 0.001
            
        if self.needs.philosophical_expression < 0.5:
            self.genes.philosophical_tendency += 0.001
            self.genes.existential_awareness += 0.001
            
        # Update animal-related skills
        if self.needs.animal_companionship < 0.5:
            self.genes.animal_affinity += 0.001
            self.genes.taming_skill += 0.001
            
        if self.needs.hunting_urge < 0.5:
            self.genes.hunting_skill += 0.001
            self.genes.strength += 0.001
            
        # Cap all skill improvements
        for gene_name in self.genes.__dict__:
            if isinstance(getattr(self.genes, gene_name), float):
                setattr(self.genes, gene_name, max(0.0, min(1.0, getattr(self.genes, gene_name))))

    def _update_philosophy(self, current_time: float, world_state: Dict) -> None:
        """Update agent's philosophical development based on experiences and environment."""
        # Get current environment and state
        environment = world_state.get("environment", {})
        terrain = environment.get_terrain_at(self.position[0], self.position[1])
        weather = environment.get_weather_at(self.position[0], self.position[1])
        
        # Only update if agent has philosophical tendency
        if self.genes.philosophical_tendency < 0.3:
            return
            
        # Update based on life experiences
        if self.age > 20:  # More likely to develop philosophy as they age
            # Consider mortality and existence
            if random.random() < 0.1:
                self.philosophy.ponder_existence({
                    "memories": self.memories,
                    "discovered_concepts": self.discovered_concepts,
                    "understanding_levels": self.understanding_levels,
                    "current_question": "What is the meaning of life?"
                })
                
        # Update based on environment
        if terrain:
            if terrain.type == TerrainType.MOUNTAIN:
                # Mountains often inspire thoughts about perspective and scale
                self.philosophy.ponder_existence({
                    "memories": self.memories,
                    "discovered_concepts": self.discovered_concepts,
                    "understanding_levels": self.understanding_levels,
                    "current_question": "How does our perspective shape our understanding?"
                })
            elif terrain.type == TerrainType.WATER:
                # Water often inspires thoughts about change and flow
                self.philosophy.ponder_existence({
                    "memories": self.memories,
                    "discovered_concepts": self.discovered_concepts,
                    "understanding_levels": self.understanding_levels,
                    "current_question": "How does change affect our existence?"
                })
                
        # Update based on weather
        if weather:
            if weather["type"] == WeatherType.THUNDERSTORM:
                # Storms often inspire thoughts about power and nature
                self.philosophy.ponder_existence({
                    "memories": self.memories,
                    "discovered_concepts": self.discovered_concepts,
                    "understanding_levels": self.understanding_levels,
                    "current_question": "What is our relationship with nature?"
                })
            elif weather["type"] == WeatherType.CLEAR:
                # Sunny weather often inspires thoughts about beauty and happiness
                self.philosophy.ponder_existence({
                    "memories": self.memories,
                    "discovered_concepts": self.discovered_concepts,
                    "understanding_levels": self.understanding_levels,
                    "current_question": "What is the nature of happiness?"
                })
            elif weather["type"] == WeatherType.WINDY:
                # Strong winds behavior
                if random.random() < 0.01:  # 1% chance to comment on weather
                    self.add_memory(
                        f"Commented on weather: {weather['intensity']}",
                        0.5,
                        {
                            "weather_type": weather["type"].value,
                            "intensity": weather["intensity"]
                        },
                        emotional_impact=0.3,
                        philosophical_impact=0.2
                    )
                
        # Update based on social interactions
        if self.needs.social < 0.3:  # If feeling lonely
            self.philosophy.ponder_existence({
                "memories": self.memories,
                "discovered_concepts": self.discovered_concepts,
                "understanding_levels": self.understanding_levels,
                "current_question": "What is the nature of human connection?"
            })
            
        # Update based on recent memories
        recent_memories = self.get_recent_memories(5)
        if recent_memories:
            # Consider philosophical implications of recent experiences
            for memory in recent_memories:
                if memory.importance > 0.7:  # Only consider significant memories
                    self.philosophy.ponder_existence({
                        "memories": self.memories,
                        "discovered_concepts": self.discovered_concepts,
                        "understanding_levels": self.understanding_levels,
                        "current_question": f"What does {memory.event} teach us about life?",
                        "context": memory.context
                    })
                    
        # Update philosophical needs
        if self.needs.philosophical_expression < 0.3:
            self.needs.philosophical_expression = min(1.0, self.needs.philosophical_expression + 0.1)

    def _calculate_compatibility(self, other_agent: Dict) -> float:
        """Calculate compatibility with another agent based on traits, values, and beliefs."""
        compatibility = 0.0
        total_weight = 0.0
        
        # Compare personality traits
        personality_traits = {
            "intelligence": 0.2,
            "social_drive": 0.15,
            "emotional_depth": 0.15,
            "creativity": 0.1,
            "philosophical_tendency": 0.1,
            "cultural_sensitivity": 0.1
        }
        
        for trait, weight in personality_traits.items():
            if trait in self.genes.__dict__ and trait in other_agent["genes"]:
                # Calculate similarity (1 - absolute difference)
                similarity = 1.0 - abs(getattr(self.genes, trait) - other_agent["genes"][trait])
                compatibility += similarity * weight
                total_weight += weight
                
        # Compare moral values if available
        if hasattr(self, 'philosophy') and 'moral_values' in other_agent:
            moral_traits = {
                "morality": 0.1,
                "free_will": 0.05,
                "determinism": 0.05,
                "spirituality": 0.05
            }
            
            for trait, weight in moral_traits.items():
                if hasattr(self.philosophy, trait) and trait in other_agent.get("philosophy", {}):
                    similarity = 1.0 - abs(getattr(self.philosophy, trait) - other_agent["philosophy"][trait])
                    compatibility += similarity * weight
                    total_weight += weight
                    
        # Compare life stage compatibility
        if hasattr(self, 'life_stage') and 'life_stage' in other_agent:
            # Adults are most compatible with other adults
            if self.life_stage == LifeStage.ADULT and other_agent["life_stage"] == "ADULT":
                compatibility += 0.1
                total_weight += 0.1
                
        # Compare social roles if available
        if hasattr(self, 'social_roles') and 'social_roles' in other_agent:
            shared_roles = set(self.social_roles) & set(other_agent["social_roles"])
            if shared_roles:
                compatibility += 0.1 * len(shared_roles)
                total_weight += 0.1
                
        # Compare tribe membership
        if hasattr(self, 'tribe') and 'tribe' in other_agent:
            if self.tribe and self.tribe == other_agent["tribe"]:
                compatibility += 0.1
                total_weight += 0.1
                
        # Normalize compatibility score
        if total_weight > 0:
            compatibility = compatibility / total_weight
            
        return min(1.0, max(0.0, compatibility))
        
    def _calculate_shared_interests(self, other_agent: Dict) -> float:
        """Calculate shared interests with another agent."""
        shared_interests = 0.0
        total_interests = 0.0
        
        # Compare discovered concepts
        if hasattr(self, 'discovered_concepts') and 'discovered_concepts' in other_agent:
            shared_concepts = self.discovered_concepts & set(other_agent["discovered_concepts"])
            if shared_concepts:
                shared_interests += 0.3 * len(shared_concepts)
                total_interests += 0.3
                
        # Compare understanding levels
        if hasattr(self, 'understanding_levels') and 'understanding_levels' in other_agent:
            shared_topics = set(self.understanding_levels.keys()) & set(other_agent["understanding_levels"].keys())
            if shared_topics:
                # Calculate average understanding similarity
                similarities = []
                for topic in shared_topics:
                    similarity = 1.0 - abs(
                        self.understanding_levels[topic] - 
                        other_agent["understanding_levels"][topic]
                    )
                    similarities.append(similarity)
                if similarities:
                    shared_interests += 0.3 * (sum(similarities) / len(similarities))
                    total_interests += 0.3
                    
        # Compare philosophical concepts
        if hasattr(self, 'philosophy') and 'philosophy' in other_agent:
            shared_concepts = set(self.philosophy.philosophical_concepts.keys()) & \
                            set(other_agent["philosophy"].get("philosophical_concepts", {}).keys())
            if shared_concepts:
                shared_interests += 0.2 * len(shared_concepts)
                total_interests += 0.2
                
        # Compare emotional concepts
        if hasattr(self, 'emotional_concepts') and 'emotional_concepts' in other_agent:
            shared_emotions = self.emotional_concepts & set(other_agent["emotional_concepts"])
            if shared_emotions:
                shared_interests += 0.2 * len(shared_emotions)
                total_interests += 0.2
                
        # Normalize shared interests score
        if total_interests > 0:
            shared_interests = shared_interests / total_interests
            
        return min(1.0, max(0.0, shared_interests))

    def _update_technology(self, current_time: float, world_state: Dict) -> None:
        """Update agent's technology and tools based on environment and needs."""
        # Get current environment
        environment = world_state.get("environment", {})
        terrain = environment.get_terrain_at(self.position[0], self.position[1])
        
        # Update tools based on terrain and needs
        if terrain:
            if terrain.type == TerrainType.FOREST:
                # Forest tools
                if "wood" not in self.tools:
                    self.tools["wood"] = {
                        "type": "axe",
                        "efficiency": 0.5,
                        "durability": 1.0
                    }
                elif self.tools["wood"]["efficiency"] < 0.8:
                    self.tools["wood"]["efficiency"] += 0.001
                    
            elif terrain.type == TerrainType.MOUNTAIN:
                # Mining tools
                if "stone" not in self.tools:
                    self.tools["stone"] = {
                        "type": "pickaxe",
                        "efficiency": 0.5,
                        "durability": 1.0
                    }
                elif self.tools["stone"]["efficiency"] < 0.8:
                    self.tools["stone"]["efficiency"] += 0.001
                    
            elif terrain.type == TerrainType.WATER:
                # Fishing tools
                if "fish" not in self.tools:
                    self.tools["fish"] = {
                        "type": "fishing_rod",
                        "efficiency": 0.5,
                        "durability": 1.0
                    }
                elif self.tools["fish"]["efficiency"] < 0.8:
                    self.tools["fish"]["efficiency"] += 0.001
                    
        # Update techniques based on tools and experience
        for tool_type, tool_data in self.tools.items():
            if tool_type not in self.techniques:
                self.techniques[tool_type] = {
                    "skill_level": 0.5,
                    "experience": 0.0,
                    "last_used": current_time
                }
            else:
                # Improve technique with use
                if current_time - self.techniques[tool_type]["last_used"] < 1000:  # Recent use
                    self.techniques[tool_type]["skill_level"] = min(1.0, 
                        self.techniques[tool_type]["skill_level"] + 0.001)
                    self.techniques[tool_type]["experience"] += 0.001
                    
        # Update tool durability
        for tool_data in self.tools.values():
            tool_data["durability"] = max(0.0, tool_data["durability"] - 0.0001)
            if tool_data["durability"] < 0.2:  # Tool needs repair
                tool_data["efficiency"] *= 0.9  # Reduced efficiency when damaged
                
        # Add memory of significant technological developments
        for tool_type, tool_data in self.tools.items():
            if tool_data["efficiency"] > 0.8 and tool_data["efficiency"] < 0.81:
                self.add_memory(
                    f"Mastered {tool_type} tool usage",
                    0.7,
                    {
                        "tool_type": tool_type,
                        "efficiency": tool_data["efficiency"],
                        "technique_level": self.techniques[tool_type]["skill_level"]
                    },
                    emotional_impact=0.4,
                    philosophical_impact=0.2
                )

    def _update_resources(self, current_time: float, world_state: Dict) -> None:
        """Update agent's resources based on environment and activities."""
        # Get current environment
        environment = world_state.get("environment", {})
        terrain = environment.get_terrain_at(self.position[0], self.position[1])
        
        # Update resources based on terrain
        if terrain:
            if terrain.type == TerrainType.FOREST:
                # Collect wood
                if "wood" not in self.inventory:
                    self.inventory["wood"] = 0.0
                self.inventory["wood"] += 0.1 * self.tools.get("wood", {}).get("efficiency", 0.5)
                
            elif terrain.type == TerrainType.MOUNTAIN:
                # Collect stone
                if "stone" not in self.inventory:
                    self.inventory["stone"] = 0.0
                self.inventory["stone"] += 0.1 * self.tools.get("stone", {}).get("efficiency", 0.5)
                
            elif terrain.type == TerrainType.WATER:
                # Collect water
                if "water" not in self.inventory:
                    self.inventory["water"] = 0.0
                self.inventory["water"] += 0.2
                
        # Update food resources
        if FoodType.RAW_MEAT.value in self.inventory:
            # Meat spoils over time
            self.inventory[FoodType.RAW_MEAT.value] = max(0.0, self.inventory[FoodType.RAW_MEAT.value] - 0.01)
            
        # Update tool resources
        for tool_type, tool_data in self.tools.items():
            if tool_data["durability"] < 0.2:
                # Need resources to repair
                if tool_type == "wood" and self.inventory.get("wood", 0) > 1.0:
                    self.inventory["wood"] -= 1.0
                    tool_data["durability"] = 1.0
                elif tool_type == "stone" and self.inventory.get("stone", 0) > 1.0:
                    self.inventory["stone"] -= 1.0
                    tool_data["durability"] = 1.0
                    
        # Add memory of significant resource changes
        for resource_type, amount in self.inventory.items():
            if amount > 10.0 and amount < 10.1:  # Just crossed threshold
                self.add_memory(
                    f"Collected significant amount of {resource_type}",
                    0.6,
                    {
                        "resource_type": resource_type,
                        "amount": amount
                    },
                    emotional_impact=0.3
                )

    def _update_health(self, current_time: float, world_state: Dict) -> None:
        """Update agent's health status."""
        # Get current environment
        environment = world_state.get("environment", {})
        weather = environment.get_weather_at(self.position[0], self.position[1])
        
        # Update health based on needs
        if self.needs.hunger < 0.2:
            self.health = max(0.0, self.health - 0.01)
        if self.needs.thirst < 0.2:
            self.health = max(0.0, self.health - 0.02)
        if self.needs.rest < 0.2:
            self.health = max(0.0, self.health - 0.005)
            
        # Update health based on weather
        if weather:
            if weather["type"] == WeatherType.RAIN:
                if self.genes.water_resistance < 0.5:
                    self.health = max(0.0, self.health - 0.01)
            elif weather["type"] == WeatherType.SNOW:
                if self.genes.cold_resistance < 0.5:
                    self.health = max(0.0, self.health - 0.02)
            elif weather["type"] == WeatherType.WINDY:
                if self.genes.dust_resistance < 0.5:
                    self.health = max(0.0, self.health - 0.01)
                    
        # Update diseases
        for disease in self.diseases[:]:  # Copy list to allow modification during iteration
            if random.random() < 0.1:  # 10% chance to recover
                self.diseases.remove(disease)
                self.add_memory(
                    f"Recovered from {disease}",
                    0.7,
                    {"disease": disease},
                    emotional_impact=0.5
                )
                
        # Update injuries
        for injury in self.injuries[:]:  # Copy list to allow modification during iteration
            if random.random() < 0.05:  # 5% chance to heal
                self.injuries.remove(injury)
                self.add_memory(
                    f"Healed from {injury}",
                    0.6,
                    {"injury": injury},
                    emotional_impact=0.4
                )
                
        # Check for death
        if self.health <= 0:
            self.die()
            
    def _update_memory(self, current_time: float, world_state: Dict) -> None:
        """Update agent's memory system."""
        # Get current environment
        environment = world_state.get("environment", {})
        terrain = environment.get_terrain_at(self.position[0], self.position[1])
        weather = environment.get_weather_at(self.position[0], self.position[1])
        
        # Add memory of significant environmental changes
        if terrain and terrain.type != self.last_terrain:
            self.add_memory(
                f"Entered {terrain.type.value} terrain",
                0.5,
                {"terrain_type": terrain.type.value},
                emotional_impact=0.3
            )
            self.last_terrain = terrain.type
            
        if weather and weather["type"] != self.last_weather:
            self.add_memory(
                f"Weather changed to {weather['type'].value}",
                0.4,
                {"weather_type": weather["type"].value},
                emotional_impact=0.2
            )
            self.last_weather = weather["type"]
            
        # Process recent memories
        recent_memories = self.get_recent_memories(5)
        for memory in recent_memories:
            if memory.importance > 0.7:
                # Update emotional state based on important memories
                self.emotions.process_experience(
                    memory.event,
                    memory.context,
                    self.to_dict()
                )
                
                # Update philosophical understanding
                if memory.philosophical_impact > 0.5:
                    self.philosophy.ponder_existence({
                        "memories": self.memories,
                        "discovered_concepts": self.discovered_concepts,
                        "understanding_levels": self.understanding_levels,
                        "current_question": f"What does {memory.event} mean?",
                        "context": memory.context
                    })
                    
    def _update_actions(self, current_time: float, world_state: Dict) -> None:
        """Update agent's actions based on current state and needs."""
        # Handle crisis situations first
        if self.crisis_state.is_crisis:
            self._handle_crisis_situation(current_time, world_state)
            return
            
        # Update behavior
        self._update_behavior(current_time, world_state)
        
        # Update relationships
        self._update_relationships(current_time, world_state)
        
        # Update skills
        self._update_skills(current_time, world_state)
        
        # Update philosophy
        self._update_philosophy(current_time, world_state)
        
        # Update animal interactions
        self._update_animal_interactions(current_time, world_state)
        
        # Update technology
        self._update_technology(current_time, world_state)
        
        # Update resources
        self._update_resources(current_time, world_state)
        
        # Update health
        self._update_health(current_time, world_state)
        
        # Update memory
        self._update_memory(current_time, world_state)

    def _seek_food(self, world_state: Dict) -> None:
        """Seek food sources."""
        food_sources = world_state.get("food_sources", [])
        if food_sources:
            nearest = min(food_sources, key=lambda f: self._calculate_distance(self.position, f["position"]))
            distance = self._calculate_distance(self.position, nearest["position"])
            
            if distance < 5:  # Within food range
                # Collect food
                food_amount = min(nearest["amount"], 1.0)
                nearest["amount"] -= food_amount
                self.inventory["food"] = self.inventory.get("food", 0) + food_amount
                self.needs.hunger = min(1.0, self.needs.hunger + 0.3)
            else:
                self._move_towards(nearest["position"])
                
    def _seek_water(self, world_state: Dict) -> None:
        """Seek water sources."""
        water_sources = world_state.get("water_sources", [])
        if water_sources:
            nearest = min(water_sources, key=lambda w: self._calculate_distance(self.position, w["position"]))
            distance = self._calculate_distance(self.position, nearest["position"])
            
            if distance < 5:  # Within water range
                # Collect water
                water_amount = min(nearest["amount"], 1.0)
                nearest["amount"] -= water_amount
                self.inventory["water"] = self.inventory.get("water", 0) + water_amount
                self.needs.thirst = min(1.0, self.needs.thirst + 0.3)
            else:
                self._move_towards(nearest["position"])
                
    def _rest(self) -> None:
        """Rest to recover energy."""
        self.needs.rest = min(1.0, self.needs.rest + 0.2)
        self.needs.energy = min(1.0, self.needs.energy + 0.1)
        
    def _seek_social_interaction(self, world_state: Dict) -> None:
        """Seek social interaction with other agents."""
        nearby_agents = self._get_nearby_agents(world_state)
        if nearby_agents:
            # Find most compatible agent
            best_agent = max(nearby_agents, key=lambda a: self._calculate_compatibility(a))
            self._interact_with_agent(best_agent)
            
    def _express_creativity(self) -> None:
        """Express creativity through various means."""
        if self.genes.creativity > 0.7:
            self.add_memory(
                "Created artistic expression",
                0.6,
                {"expression_type": "art"},
                emotional_impact=0.4,
                philosophical_impact=0.2
            )
            self.needs.creative_expression = min(1.0, self.needs.creative_expression + 0.3)
            
    def _express_philosophy(self) -> None:
        """Express philosophical thoughts."""
        if self.genes.philosophical_tendency > 0.7:
            self.philosophy.ponder_existence({
                "memories": self.memories,
                "discovered_concepts": self.discovered_concepts,
                "understanding_levels": self.understanding_levels,
                "current_question": "What is the meaning of existence?"
            })
            self.needs.philosophical_expression = min(1.0, self.needs.philosophical_expression + 0.3)
            
    def _interact_with_agent(self, other_agent: Dict) -> None:
        """Interact with another agent."""
        # Update relationship
        if other_agent["id"] not in self.relationships:
            self.relationships[other_agent["id"]] = {
                "compatibility": self._calculate_compatibility(other_agent),
                "attraction": self._calculate_attraction(other_agent),
                "shared_interests": self._calculate_shared_interests(other_agent),
                "trust": 0.5,
                "affection": 0.5,
                "last_interaction": time.time()
            }
            
        # Update social need
        self.needs.social = min(1.0, self.needs.social + 0.2)
        
        # Add memory of interaction
        self.add_memory(
            f"Interacted with {other_agent['name']}",
            0.5,
            {
                "agent_id": other_agent["id"],
                "agent_name": other_agent["name"],
                "interaction_type": "social"
            },
            emotional_impact=0.3
        )
        
    def _update_fishing_knowledge(self, world_state: Dict):
        """Update fishing knowledge based on experience."""
        # Get current conditions
        current_season = world_state["weather"]["season"]
        current_time = world_state["time"]
        current_position = self.position
        
        # Update best seasons
        if self._is_good_fishing_spot(current_position, world_state):
            self.fishing_knowledge["best_seasons"].add(current_season)
            
        # Update best times
        if self._is_good_fishing_time(current_time):
            self.fishing_knowledge["best_times"].add(current_time.hour)
            
        # Update best locations
        if self._is_good_fishing_spot(current_position, world_state):
            self.known_fishing_spots.add(current_position)
            
    def _update_fishing_skill(self, time_delta: float):
        """Update fishing skill based on practice and success."""
        # Base skill increase from practice
        skill_increase = 0.001 * time_delta
        
        # Additional increase from successful catches
        successful_catches = sum(1 for activity in self.fishing_history[-10:]
                               if activity["success"] and activity["time"] > self.last_update)
        skill_increase += 0.01 * successful_catches
        
        # Update skill
        self.fishing_skill = min(1.0, self.fishing_skill + skill_increase)
        
    def _is_good_fishing_time(self, time: datetime) -> bool:
        """Check if current time is good for fishing."""
        hour = time.hour
        
        # Best fishing times are dawn and dusk
        return 5 <= hour <= 7 or 17 <= hour <= 19
        
    def craft_fishing_tool(self, tool_type: str) -> bool:
        """Craft a fishing tool."""
        # Check if agent has required resources
        required_resources = {
            "net": [(ResourceType.FIBER, 5)],
            "rod": [(ResourceType.WOOD, 2), (ResourceType.FIBER, 1)],
            "spear": [(ResourceType.WOOD, 1), (ResourceType.STONE, 1)],
            "trap": [(ResourceType.WOOD, 3), (ResourceType.FIBER, 2)]
        }.get(tool_type, [])
        
        if not required_resources:
            return False
            
        # Check if agent has resources
        for resource_type, amount in required_resources:
            if resource_type not in self.inventory or self.inventory[resource_type] < amount:
                return False
                
        # Consume resources
        for resource_type, amount in required_resources:
            self.inventory[resource_type] -= amount
            
        # Create tool
        tool_id = f"fishing_tool_{len(self.fishing_tools)}"
        self.fishing_tools[tool_id] = {
            "type": tool_type,
            "durability": 1.0,
            "efficiency": random.uniform(0.8, 1.0)
        }
        
        return True
        
    def repair_fishing_tool(self, tool_id: str) -> bool:
        """Repair a fishing tool."""
        if tool_id not in self.fishing_tools:
            return False
            
        tool = self.fishing_tools[tool_id]
        if tool["durability"] >= 1.0:
            return False
            
        # Check if agent has required resources
        required_resources = {
            "net": [(ResourceType.FIBER, 2)],
            "rod": [(ResourceType.WOOD, 1), (ResourceType.FIBER, 1)],
            "spear": [(ResourceType.WOOD, 1)],
            "trap": [(ResourceType.WOOD, 1), (ResourceType.FIBER, 1)]
        }.get(tool["type"], [])
        
        if not required_resources:
            return False
            
        # Check if agent has resources
        for resource_type, amount in required_resources:
            if resource_type not in self.inventory or self.inventory[resource_type] < amount:
                return False
                
        # Consume resources
        for resource_type, amount in required_resources:
            self.inventory[resource_type] -= amount
            
        # Repair tool
        tool["durability"] = 1.0
        
        return True

    def _calculate_distance(self, other: 'Agent') -> float:
        """Calculate distance to another agent using Haversine formula"""
        return self.world.get_distance(self.longitude, self.latitude, other.longitude, other.latitude)

    def _move_towards(self, target_lon: float, target_lat: float, speed: float = 1.0) -> None:
        """Move towards a target position"""
        # Calculate direction
        dx = target_lon - self.longitude
        dy = target_lat - self.latitude
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize and scale by speed
            dx = (dx / distance) * speed
            dy = (dy / distance) * speed
            
            # Update position
            self.longitude += dx
            self.latitude += dy
            
            # Keep within bounds
            self.longitude = (self.longitude + 180) % 360 - 180
            self.latitude = max(-90, min(90, self.latitude))

    def _get_nearby_agents(self, radius: float) -> List['Agent']:
        """Get all agents within radius"""
        nearby = []
        for agent in self.world.agents.values():
            if agent.id != self.id:
                distance = self._calculate_distance(agent)
                if distance <= radius:
                    nearby.append(agent)
        return nearby

    def _get_nearby_resources(self, radius: float) -> List[Resource]:
        """Get all resources within radius"""
        nearby = []
        for resource in self.world.resources.get_resources():
            distance = self.world.get_distance(
                self.longitude, self.latitude,
                resource.longitude, resource.latitude
            )
            if distance <= radius:
                nearby.append(resource)
        return nearby
