from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import random
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ArtType(Enum):
    ORAL = "oral"  # Stories, songs, poems
    VISUAL = "visual"  # Paintings, carvings, sculptures
    PERFORMANCE = "performance"  # Dance, theater, rituals
    WRITTEN = "written"  # Written stories, poems, plays

class MythType(Enum):
    CREATION = "creation"  # Origin stories
    HERO = "hero"  # Heroic tales
    MORAL = "moral"  # Moral lessons
    NATURAL = "natural"  # Natural phenomena
    RELIGIOUS = "religious"  # Religious beliefs
    HISTORICAL = "historical"  # Historical events

@dataclass
class Artwork:
    title: str
    type: ArtType
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    materials: List[str] = field(default_factory=list)
    techniques: List[str] = field(default_factory=list)
    cultural_significance: float = 0.0  # 0-1 scale
    emotional_impact: float = 0.0  # 0-1 scale
    complexity: float = 0.0  # 0-1 scale
    popularity: float = 0.0  # 0-1 scale
    preservation_state: float = 1.0  # 0-1 scale
    location: Optional[Tuple[float, float]] = None
    audience: Set[str] = field(default_factory=set)  # Set of agent IDs
    influences: List[str] = field(default_factory=list)  # List of artwork IDs
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Myth:
    title: str
    type: MythType
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    story: str = ""
    characters: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    cultural_significance: float = 0.0  # 0-1 scale
    emotional_impact: float = 0.0  # 0-1 scale
    complexity: float = 0.0  # 0-1 scale
    popularity: float = 0.0  # 0-1 scale
    preservation_state: float = 1.0  # 0-1 scale
    location: Optional[Tuple[float, float]] = None
    audience: Set[str] = field(default_factory=set)  # Set of agent IDs
    influences: List[str] = field(default_factory=list)  # List of myth IDs
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class CulturalNarrative:
    title: str
    creator: str  # Agent ID
    creation_date: float = field(default_factory=time.time)
    description: str = ""
    themes: List[str] = field(default_factory=list)
    cultural_significance: float = 0.0  # 0-1 scale
    emotional_impact: float = 0.0  # 0-1 scale
    complexity: float = 0.0  # 0-1 scale
    popularity: float = 0.0  # 0-1 scale
    preservation_state: float = 1.0  # 0-1 scale
    location: Optional[Tuple[float, float]] = None
    audience: Set[str] = field(default_factory=set)  # Set of agent IDs
    influences: List[str] = field(default_factory=list)  # List of narrative IDs
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

class MythologySystem:
    def __init__(self, world):
        """Initialize the mythology system."""
        self.world = world
        self.artworks: Dict[str, Artwork] = {}
        self.myths: Dict[str, Myth] = {}
        self.narratives: Dict[str, CulturalNarrative] = {}
        self.initialize_system()
        
    def initialize_system(self):
        """Initialize the mythology system with basic capabilities."""
        logger.info("Initializing mythology system...")
        
        # Create initial myths and art
        self._create_initial_myths()
        self._create_initial_art()
        
        logger.info("Mythology system initialization complete")
        
    def _create_initial_myths(self):
        """Create initial myths based on natural phenomena."""
        initial_myths = [
            ("The First Fire", MythType.CREATION, 
             "How the first fire was discovered and shared"),
            ("The Great Flood", MythType.NATURAL,
             "A story about a great flood that changed the land"),
            ("The Wise Elder", MythType.HERO,
             "Tales of a wise elder who taught the people"),
            ("The Sun and Moon", MythType.NATURAL,
             "How the sun and moon came to be")
        ]
        
        for title, type_, story in initial_myths:
            myth = Myth(
                title=title,
                type=type_,
                creator="system",
                story=story,
                cultural_significance=0.5,
                emotional_impact=0.5,
                complexity=0.3,
                popularity=0.5
            )
            self.myths[title] = myth
            
    def _create_initial_art(self):
        """Create initial art forms."""
        initial_art = [
            ("Cave Paintings", ArtType.VISUAL,
             "Early paintings on cave walls"),
            ("Storytelling", ArtType.ORAL,
             "Oral traditions passed down through generations"),
            ("Ritual Dance", ArtType.PERFORMANCE,
             "Ceremonial dances for important events")
        ]
        
        for title, type_, description in initial_art:
            artwork = Artwork(
                title=title,
                type=type_,
                creator="system",
                description=description,
                cultural_significance=0.5,
                emotional_impact=0.5,
                complexity=0.3,
                popularity=0.5
            )
            self.artworks[title] = artwork
            
    def create_artwork(self, title: str, type_: ArtType, creator: str,
                      description: str = "", location: Optional[Tuple[float, float]] = None) -> Artwork:
        """Create a new artwork."""
        if title in self.artworks:
            logger.warning(f"Artwork {title} already exists")
            return self.artworks[title]
            
        artwork = Artwork(
            title=title,
            type=type_,
            creator=creator,
            description=description,
            location=location
        )
        
        self.artworks[title] = artwork
        logger.info(f"Created new artwork: {title}")
        return artwork
        
    def create_myth(self, title: str, type_: MythType, creator: str,
                   story: str = "", location: Optional[Tuple[float, float]] = None) -> Myth:
        """Create a new myth."""
        if title in self.myths:
            logger.warning(f"Myth {title} already exists")
            return self.myths[title]
            
        myth = Myth(
            title=title,
            type=type_,
            creator=creator,
            story=story,
            location=location
        )
        
        self.myths[title] = myth
        logger.info(f"Created new myth: {title}")
        return myth
        
    def create_narrative(self, title: str, creator: str,
                        description: str = "", location: Optional[Tuple[float, float]] = None) -> CulturalNarrative:
        """Create a new cultural narrative."""
        if title in self.narratives:
            logger.warning(f"Narrative {title} already exists")
            return self.narratives[title]
            
        narrative = CulturalNarrative(
            title=title,
            creator=creator,
            description=description,
            location=location
        )
        
        self.narratives[title] = narrative
        logger.info(f"Created new narrative: {title}")
        return narrative
        
    def add_audience(self, title: str, agent_id: str, category: str = "artwork"):
        """Add an audience member to an artwork, myth, or narrative."""
        if category == "artwork" and title in self.artworks:
            self.artworks[title].audience.add(agent_id)
        elif category == "myth" and title in self.myths:
            self.myths[title].audience.add(agent_id)
        elif category == "narrative" and title in self.narratives:
            self.narratives[title].audience.add(agent_id)
            
    def remove_audience(self, title: str, agent_id: str, category: str = "artwork"):
        """Remove an audience member from an artwork, myth, or narrative."""
        if category == "artwork" and title in self.artworks:
            self.artworks[title].audience.discard(agent_id)
        elif category == "myth" and title in self.myths:
            self.myths[title].audience.discard(agent_id)
        elif category == "narrative" and title in self.narratives:
            self.narratives[title].audience.discard(agent_id)
            
    def evolve_artwork(self, title: str, time_delta: float):
        """Evolve an artwork over time."""
        if title not in self.artworks:
            return
            
        artwork = self.artworks[title]
        
        # Update popularity based on audience size
        audience_factor = min(1.0, len(artwork.audience) / 100.0)
        artwork.popularity = (artwork.popularity * 0.9 + audience_factor * 0.1)
        
        # Update preservation state
        artwork.preservation_state = max(0.0, 
            artwork.preservation_state - 0.001 * time_delta)
            
        # Update cultural significance
        if len(artwork.audience) > 0:
            artwork.cultural_significance = min(1.0,
                artwork.cultural_significance + 0.01 * time_delta)
                
    def evolve_myth(self, title: str, time_delta: float):
        """Evolve a myth over time."""
        if title not in self.myths:
            return
            
        myth = self.myths[title]
        
        # Update popularity based on audience size
        audience_factor = min(1.0, len(myth.audience) / 100.0)
        myth.popularity = (myth.popularity * 0.9 + audience_factor * 0.1)
        
        # Update preservation state
        myth.preservation_state = max(0.0,
            myth.preservation_state - 0.0005 * time_delta)  # Myths decay slower than art
            
        # Update cultural significance
        if len(myth.audience) > 0:
            myth.cultural_significance = min(1.0,
                myth.cultural_significance + 0.01 * time_delta)
                
    def evolve_narrative(self, title: str, time_delta: float):
        """Evolve a cultural narrative over time."""
        if title not in self.narratives:
            return
            
        narrative = self.narratives[title]
        
        # Update popularity based on audience size
        audience_factor = min(1.0, len(narrative.audience) / 100.0)
        narrative.popularity = (narrative.popularity * 0.9 + audience_factor * 0.1)
        
        # Update preservation state
        narrative.preservation_state = max(0.0,
            narrative.preservation_state - 0.0003 * time_delta)  # Narratives decay slowest
            
        # Update cultural significance
        if len(narrative.audience) > 0:
            narrative.cultural_significance = min(1.0,
                narrative.cultural_significance + 0.01 * time_delta)
                
    def update(self, time_delta: float):
        """Update mythology system state."""
        # Evolve artworks
        for title in list(self.artworks.keys()):
            self.evolve_artwork(title, time_delta)
            
        # Evolve myths
        for title in list(self.myths.keys()):
            self.evolve_myth(title, time_delta)
            
        # Evolve narratives
        for title in list(self.narratives.keys()):
            self.evolve_narrative(title, time_delta)
            
    def to_dict(self) -> Dict:
        """Convert mythology system state to dictionary for serialization."""
        return {
            "artworks": {
                title: {
                    "title": artwork.title,
                    "type": artwork.type.value,
                    "creator": artwork.creator,
                    "creation_date": artwork.creation_date,
                    "description": artwork.description,
                    "materials": artwork.materials,
                    "techniques": artwork.techniques,
                    "cultural_significance": artwork.cultural_significance,
                    "emotional_impact": artwork.emotional_impact,
                    "complexity": artwork.complexity,
                    "popularity": artwork.popularity,
                    "preservation_state": artwork.preservation_state,
                    "location": artwork.location,
                    "audience": list(artwork.audience),
                    "influences": artwork.influences,
                    "created_at": artwork.created_at,
                    "last_update": artwork.last_update
                }
                for title, artwork in self.artworks.items()
            },
            "myths": {
                title: {
                    "title": myth.title,
                    "type": myth.type.value,
                    "creator": myth.creator,
                    "creation_date": myth.creation_date,
                    "story": myth.story,
                    "characters": myth.characters,
                    "themes": myth.themes,
                    "cultural_significance": myth.cultural_significance,
                    "emotional_impact": myth.emotional_impact,
                    "complexity": myth.complexity,
                    "popularity": myth.popularity,
                    "preservation_state": myth.preservation_state,
                    "location": myth.location,
                    "audience": list(myth.audience),
                    "influences": myth.influences,
                    "created_at": myth.created_at,
                    "last_update": myth.last_update
                }
                for title, myth in self.myths.items()
            },
            "narratives": {
                title: {
                    "title": narrative.title,
                    "creator": narrative.creator,
                    "creation_date": narrative.creation_date,
                    "description": narrative.description,
                    "themes": narrative.themes,
                    "cultural_significance": narrative.cultural_significance,
                    "emotional_impact": narrative.emotional_impact,
                    "complexity": narrative.complexity,
                    "popularity": narrative.popularity,
                    "preservation_state": narrative.preservation_state,
                    "location": narrative.location,
                    "audience": list(narrative.audience),
                    "influences": narrative.influences,
                    "created_at": narrative.created_at,
                    "last_update": narrative.last_update
                }
                for title, narrative in self.narratives.items()
            }
        } 